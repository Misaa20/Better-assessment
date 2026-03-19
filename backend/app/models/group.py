from datetime import datetime, timezone

from app import db


class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    members = db.relationship("Member", back_populates="group", cascade="all, delete-orphan")
    expenses = db.relationship("Expense", back_populates="group", cascade="all, delete-orphan")
    settlements = db.relationship("Settlement", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Group {self.id}: {self.name}>"


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    group = db.relationship("Group", back_populates="members")
    expenses_paid = db.relationship("Expense", back_populates="paid_by_member")
    splits = db.relationship("ExpenseSplit", back_populates="member")

    __table_args__ = (
        db.UniqueConstraint("name", "group_id", name="uq_member_name_per_group"),
    )

    def __repr__(self):
        return f"<Member {self.id}: {self.name}>"
