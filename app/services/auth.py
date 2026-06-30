from sqlalchemy.orm import Session
from app.models.user import Users
from app.core.security import hash_password, verify_password


def get_user_by_email(db: Session, email: str) -> Users | None:
    return db.query(Users).filter(Users.email == email).first()


def create_user(db: Session, email: str, password: str) -> Users:
    user = Users(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Users | None:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
