# AttendX — Smart Attendance Prototype

A hackathon starter with:
- Responsive student/teacher web UI (works on mobile browsers too)
- FastAPI backend
- SQLite database for easy local setup
- Time-limited signed QR tokens
- QR code image display for teacher sessions
- Duplicate-attendance prevention
- CSV export (opens in Excel)
- Demo seed data and API docs

## Run backend (Python 3.10+)
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Windows: copy .env.example .env
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000/docs

## Run frontend (Node 20+)
In a second terminal:
```bash
cd frontend
npm install
npm run dev
```
Open the URL printed by Vite (normally http://localhost:5173).

The UI starts in demo mode and can connect to the backend using the API Base URL field.
Seed demo records:
```bash
cd backend
python -m app.seed
```

## Demo flow
1. Seed demo data.
2. In the UI choose Teacher, select a lecture and click Start lecture / Generate QR.
3. Copy the QR token or display the generated QR.
4. In Student mode enter student ID `1`, scan the QR using a camera-capable browser or paste the token in the demo field.
5. Teacher dashboard refreshes attendance and CSV export is available.

## Important production work still required
This is a functional hackathon prototype, not a production biometric system. Before real college deployment:
- Add role-based authentication, HTTPS, rate limits, CSRF/CORS restrictions and audit logging.
- Implement consent-based face enrollment and a vetted on-device/server-side face verification + presentation-attack detection solution. Do not treat a face match as proof by itself.
- Do not store raw face images. Store encrypted biometric templates with strict access controls and retention/deletion policies.
- Add classroom-side challenge / teacher confirmation. QR alone can be forwarded; GPS/Bluetooth/Wi-Fi are supporting signals, not proof.
- Provide an accessible manual fallback and an appeal/correction process.
- Follow applicable privacy and biometric-data laws and college policy.

The included QR token is short-lived and signed, and the teacher dashboard can display it as a QR image. The demo endpoint intentionally accepts a student ID for easy testing. It is NOT secure authentication.
