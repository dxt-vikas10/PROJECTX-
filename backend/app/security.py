import os, time, hmac, hashlib
from dotenv import load_dotenv
load_dotenv()
SECRET = os.getenv("QR_SECRET", "local-demo-secret-change-me")
TTL = int(os.getenv("QR_TTL_SECONDS", "30"))

def create_token(lecture_id: int) -> str:
    bucket = int(time.time()) // TTL
    payload = f"{lecture_id}.{bucket}"
    sig = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}.{sig}"

def verify_token(token: str, lecture_id: int) -> bool:
    try:
        raw_lecture, raw_bucket, signature = token.split(".")
        bucket = int(raw_bucket)
        if int(raw_lecture) != lecture_id:
            return False
        current = int(time.time()) // TTL
        if bucket not in (current, current - 1):
            return False
        payload = f"{lecture_id}.{bucket}"
        expected = hmac.new(SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    except (ValueError, TypeError):
        return False
