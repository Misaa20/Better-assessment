import pytest

from app import create_app, db as _db
from app.models import Group, Member


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_group(app, db):
    """Create a group with three members for testing."""
    group = Group(name="Test Group")
    alice = Member(name="Alice", group=group)
    bob = Member(name="Bob", group=group)
    charlie = Member(name="Charlie", group=group)
    db.session.add(group)
    db.session.commit()
    return {
        "group": group,
        "alice": alice,
        "bob": bob,
        "charlie": charlie,
    }
