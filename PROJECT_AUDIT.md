# AttendX project audit — updated starter

## Improvements in this revision
- Removed the duplicated Classroom input that appeared in the teacher form.
- Kept Subject and Classroom editable, with placeholders and length limits.
- Added backend validation for blank/oversized subject and classroom values.
- Added a QR PNG endpoint and teacher-side QR image display.
- Added both localhost and 127.0.0.1 to local development CORS origins.
- Added a clearer attendance-save conflict response for duplicate/racing submissions.
- Kept the short-lived signed QR token and demo duplicate-attendance rule.

## Still not implemented (do not present these as finished)
- Real teacher/student accounts, passwords, role-based authorization.
- Real camera scanning in the student portal.
- Face recognition, liveness or anti-spoofing.
- Classroom proximity proof; QR can still be forwarded.
- Production deployment, HTTPS, secret management, rate limiting, monitoring and formal privacy review.

## Important privacy and safety note
Do not collect face images or biometric data for a hackathon demo. Any future biometric feature needs informed consent, a non-biometric alternative, minimal retention, strong access controls and review against applicable law and school policy.
