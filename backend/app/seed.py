from .database import Base, engine, SessionLocal
from .models import Student, Teacher, Lecture
Base.metadata.create_all(bind=engine)
db = SessionLocal()
if not db.query(Teacher).first():
    db.add(Teacher(name="Demo Teacher", email="teacher@attendx.demo"))
if not db.query(Student).first():
    db.add_all([
        Student(roll_number="AX001", name="Aarav Sharma"),
        Student(roll_number="AX002", name="Aditi Verma"),
        Student(roll_number="AX003", name="Kabir Singh"),
        Student(roll_number="AX004", name="Meera Gupta"),
    ])
db.commit()
if not db.query(Lecture).first():
    db.add(Lecture(subject="Artificial Intelligence", classroom="Room 204", teacher_id=1))
    db.commit()
print("Demo data ready. Teacher ID=1, Lecture ID=1, Student IDs=1..4")
db.close()
