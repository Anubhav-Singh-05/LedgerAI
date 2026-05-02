from passlib.context import CryptContext
from core.database import SessionLocal
from core.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    password = password[:72]   # ✅ FIX
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    password = password[:72]   # ✅ FIX
    return pwd_context.verify(password, hashed)


def signup_user(email: str, password: str):
    db = SessionLocal()

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        db.close()
        return None, "User already exists"

    user = User(
        email=email,
        password=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()

    return user, None


def login_user(email: str, password: str):
    db = SessionLocal()

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        db.close()
        return None, "Invalid credentials"

    db.close()
    return user, None