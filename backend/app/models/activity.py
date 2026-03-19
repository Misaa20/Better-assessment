from datetime import datetime, timezone

from app import db


class Activity(db.Model):
    __tablename__ = "activities"

    ACTION_GROUP_CREATED = "group_created"
    ACTION_MEMBER_ADDED = "member_added"
    ACTION_EXPENSE_ADDED = "expense_added"
    ACTION_EXPENSE_VOIDED = "expense_voided"
    ACTION_SETTLEMENT_MADE = "settlement_made"

    VALID_ACTIONS = {
        ACTION_GROUP_CREATED,
        ACTION_MEMBER_ADDED,
        ACTION_EXPENSE_ADDED,
        ACTION_EXPENSE_VOIDED,
        ACTION_SETTLEMENT_MADE,
    }

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    action = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    group = db.relationship(
        "Group",
        backref=db.backref("activities", lazy="dynamic", cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<Activity {self.id}: {self.action}>"
