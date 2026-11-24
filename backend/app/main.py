import csv, io
from fastapi.responses import Response
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select
from .database import Base, engine, get_db
from .models import Student, Teacher, Lecture, Attendance
from .security import create_token, verify_token

Base.metadata.create_all(bind=engine)
app = FastAPI(title="AttendX API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def health():
    return {"app": "AttendX", "status": "running", "note": "Hackathon prototype"}

@app.get("/students")
def students(db: Session = Depends(get_db)):
    return [{"id": s.id, "roll_number": s.roll_number, "name": s.name, "department": s.department}
            for s in db.scalars(select(Student).order_by(Student.id)).all()]

@app.get("/lectures")
def lectures(db: Session = Depends(get_db)):
    return [{"id": l.id, "subject": l.subject, "classroom": l.classroom, "active": l.active}
            for l in db.scalars(select(Lecture).order_by(Lecture.id.desc())).all()]

@app.post("/lectures")
def create_lecture(subject: str, classroom: str, teacher_id: int = 1, db: Session = Depends(get_db)):
    subject = subject.strip()
    classroom = classroom.strip()
    if not subject or len(subject) > 120:
        raise HTTPException(422, "Subject is required and must be 120 characters or fewer.")
    if not classroom or len(classroom) > 80:
        raise HTTPException(422, "Classroom is required and must be 80 characters or fewer.")
    if not db.get(Teacher, teacher_id):
        raise HTTPException(404, "Teacher not found. Run demo seed first.")
    lecture = Lecture(subject=subject, classroom=classroom, teacher_id=teacher_id)
    db.add(lecture); db.commit(); db.refresh(lecture)
    return {"id": lecture.id, "subject": lecture.subject, "classroom": lecture.classroom}

@app.post("/lectures/{lecture_id}/close")
def close_lecture(lecture_id: int, db: Session = Depends(get_db)):
    lecture = db.get(Lecture, lecture_id)
    if not lecture: raise HTTPException(404, "Lecture not found")
    lecture.active = False; db.commit()
    return {"message": "Lecture closed"}

@app.get("/lectures/{lecture_id}/qr")
def lecture_qr(lecture_id: int, db: Session = Depends(get_db)):
    lecture = db.get(Lecture, lecture_id)
    if not lecture or not lecture.active: raise HTTPException(404, "Active lecture not found")
    return {"lecture_id": lecture_id, "token": create_token(lecture_id), "ttl_seconds": 30}

@app.get("/lectures/{lecture_id}/qr-image")
def lecture_qr_image(lecture_id: int, token: str, db: Session = Depends(get_db)):
    lecture = db.get(Lecture, lecture_id)
    if not lecture or not lecture.active:
        raise HTTPException(404, "Active lecture not found")
    if not verify_token(token, lecture_id):
        raise HTTPException(400, "QR token invalid or expired. Generate a fresh token.")
    import qrcode
    image = qrcode.make(token)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return Response(content=buffer.getvalue(), media_type="image/png",
                    headers={"Cache-Control": "no-store, max-age=0"})

@app.post("/attendance")
def mark_attendance(student_id: int, lecture_id: int, token: str, db: Session = Depends(get_db)):
    student, lecture = db.get(Student, student_id), db.get(Lecture, lecture_id)
    if not student or not lecture or not lecture.active:
        raise HTTPException(404, "Student or active lecture not found")
    if not verify_token(token, lecture_id):
        raise HTTPException(400, "QR token invalid or expired")
    existing = db.scalar(select(Attendance).where(
        Attendance.student_id == student_id, Attendance.lecture_id == lecture_id))
    if existing: raise HTTPException(409, "Attendance already marked")
    record = Attendance(student_id=student_id, lecture_id=lecture_id)
    db.add(record)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(409, "Attendance already marked or could not be saved. Refresh and try again.")
    db.refresh(record)
    return {"message": "Attendance marked", "student": student.name, "roll_number": student.roll_number,
            "status": record.status, "marked_at": record.marked_at.isoformat()}

@app.get("/attendance")
def attendance(db: Session = Depends(get_db)):
    rows = db.execute(select(Attendance, Student, Lecture)
        .join(Student, Attendance.student_id == Student.id)
        .join(Lecture, Attendance.lecture_id == Lecture.id)
        .order_by(Attendance.id.desc())).all()
    return [{"id": a.id, "student_id": s.id, "roll_number": s.roll_number, "student": s.name,
             "subject": l.subject, "classroom": l.classroom, "marked_at": a.marked_at.isoformat(),
             "status": a.status, "verification": a.verification} for a,s,l in rows]

@app.get("/attendance/export")
def export_csv(db: Session = Depends(get_db)):
    rows = db.execute(select(Attendance, Student, Lecture)
        .join(Student, Attendance.student_id == Student.id)
        .join(Lecture, Attendance.lecture_id == Lecture.id)).all()
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Roll Number","Student Name","Subject","Classroom","Marked At","Status","Verification"])
    for a,s,l in rows:
        writer.writerow([s.roll_number,s.name,l.subject,l.classroom,a.marked_at.isoformat(),a.status,a.verification])
    return StreamingResponse(iter([out.getvalue()]), media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="attendx-report.csv"'})
