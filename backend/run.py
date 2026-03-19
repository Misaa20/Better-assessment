from app import create_app, db

app = create_app()


def seed():
    from app.services import group_service, expense_service
    from app.models import Group

    if Group.query.first():
        return

    group = group_service.create_group("Weekend Trip", ["Alice", "Bob", "Charlie"])
    members = {m.name: m.id for m in group.members}

    expense_service.create_expense(
        group_id=group.id,
        description="Dinner",
        amount=90.00,
        paid_by=members["Alice"],
        split_type="equal",
        splits_data=[{"member_id": mid} for mid in members.values()],
    )
    expense_service.create_expense(
        group_id=group.id,
        description="Uber",
        amount=24.00,
        paid_by=members["Bob"],
        split_type="exact",
        splits_data=[
            {"member_id": members["Alice"], "amount": 8.00},
            {"member_id": members["Bob"], "amount": 8.00},
            {"member_id": members["Charlie"], "amount": 8.00},
        ],
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed()
    app.run(debug=True, port=5001)
