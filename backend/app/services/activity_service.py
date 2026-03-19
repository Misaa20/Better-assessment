from app import db
from app.models import Activity


def record(group_id: int, action: str, description: str) -> Activity:
    activity = Activity(
        group_id=group_id,
        action=action,
        description=description,
    )
    db.session.add(activity)
    return activity


def list_activities(group_id: int, limit: int = 50) -> list[Activity]:
    return (
        Activity.query
        .filter_by(group_id=group_id)
        .order_by(Activity.created_at.desc())
        .limit(limit)
        .all()
    )
