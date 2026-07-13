from sqlalchemy.orm import Session
from app.models import Member, MemberRole


def register_member(db: Session, name: str, email: str, hashed_password: str, role = None) -> Member:
    existing = db.query(Member).filter(Member.email == email).first()
    if existing:
        if not existing.is_active:
            existing.name = name
            existing.hashed_password = hashed_password
            if role:
                existing.role = role
            existing.is_active = True
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise ValueError(f"Member with email '{email}' already registered.")

    db_member = Member(
        name=name,
        email=email,
        hashed_password=hashed_password,
        role=role or MemberRole.MEMBER,
        is_active=True
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def get_member(db: Session, member_id: int) -> Member:
    return db.query(Member).filter(Member.id == member_id).first()
