from datetime import datetime, timezone

from app import db


class Settlement(db.Model):
    __tablename__ = "settlements"

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    paid_by = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    paid_to = db.Column(db.Integer, db.ForeignKey("members.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    group = db.relationship("Group", back_populates="settlements")
    payer = db.relationship("Member", foreign_keys=[paid_by])
    payee = db.relationship("Member", foreign_keys=[paid_to])

    __table_args__ = (
        db.CheckConstraint("amount > 0", name="ck_settlement_positive_amount"),
        db.CheckConstraint("paid_by != paid_to", name="ck_settlement_different_members"),
    )

    def __repr__(self):
        return f"<Settlement {self.id}: {self.amount}>"
