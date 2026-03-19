from datetime import datetime, timezone

from app import db


class Expense(db.Model):
    __tablename__ = "expenses"

    SPLIT_EQUAL = "equal"
    SPLIT_EXACT = "exact"
    SPLIT_PERCENTAGE = "percentage"
    VALID_SPLIT_TYPES = {SPLIT_EQUAL, SPLIT_EXACT, SPLIT_PERCENTAGE}

    STATUS_ACTIVE = "active"
    STATUS_VOIDED = "voided"
    VALID_STATUSES = {STATUS_ACTIVE, STATUS_VOIDED}

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    split_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_ACTIVE)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    paid_by = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    group = db.relationship("Group", back_populates="expenses")
    paid_by_member = db.relationship("Member", back_populates="expenses_paid")
    splits = db.relationship("ExpenseSplit", back_populates="expense", cascade="all, delete-orphan")

    __table_args__ = (
        db.CheckConstraint("amount > 0", name="ck_expense_positive_amount"),
        db.CheckConstraint(
            f"split_type IN ('{SPLIT_EQUAL}', '{SPLIT_EXACT}', '{SPLIT_PERCENTAGE}')",
            name="ck_expense_valid_split_type",
        ),
        db.CheckConstraint(
            f"status IN ('{STATUS_ACTIVE}', '{STATUS_VOIDED}')",
            name="ck_expense_valid_status",
        ),
    )

    def __repr__(self):
        return f"<Expense {self.id}: {self.description} ({self.amount})>"


class ExpenseSplit(db.Model):
    __tablename__ = "expense_splits"

    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey("expenses.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)

    expense = db.relationship("Expense", back_populates="splits")
    member = db.relationship("Member", back_populates="splits")

    __table_args__ = (
        db.CheckConstraint("amount >= 0", name="ck_split_non_negative_amount"),
        db.UniqueConstraint("expense_id", "member_id", name="uq_one_split_per_member"),
    )
