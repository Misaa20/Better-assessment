"""Integration tests for the full API request/response cycle."""

import json


class TestGroupAPI:
    def test_create_group(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Trip"
        assert len(data["members"]) == 2

    def test_create_group_rejects_single_member(self, client):
        resp = client.post("/api/groups", json={
            "name": "Solo",
            "members": ["Alice"],
        })
        assert resp.status_code == 422

    def test_create_group_rejects_duplicate_members(self, client):
        resp = client.post("/api/groups", json={
            "name": "Dupes",
            "members": ["Alice", "Alice"],
        })
        assert resp.status_code == 422

    def test_list_groups(self, client):
        client.post("/api/groups", json={"name": "A", "members": ["X", "Y"]})
        client.post("/api/groups", json={"name": "B", "members": ["X", "Y"]})

        resp = client.get("/api/groups")
        assert resp.status_code == 200
        assert len(resp.get_json()["groups"]) == 2

    def test_get_group(self, client):
        create = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        group_id = create.get_json()["id"]

        resp = client.get(f"/api/groups/{group_id}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Trip"

    def test_get_nonexistent_group(self, client):
        resp = client.get("/api/groups/9999")
        assert resp.status_code == 404

    def test_delete_group_with_zero_balances(self, client):
        create = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        group_id = create.get_json()["id"]

        resp = client.delete(f"/api/groups/{group_id}")
        assert resp.status_code == 204

    def test_delete_group_rejects_unsettled_balances(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        data = resp.get_json()
        gid = data["id"]
        members = {m["name"]: m["id"] for m in data["members"]}

        client.post("/api/expenses", json={
            "description": "Dinner",
            "amount": 100.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "equal",
            "splits": [
                {"member_id": members["Alice"]},
                {"member_id": members["Bob"]},
            ],
        })

        resp = client.delete(f"/api/groups/{gid}")
        assert resp.status_code == 400
        assert resp.get_json()["code"] == "GROUP_NOT_SETTLED"


class TestExpenseAPI:
    def _create_group(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob", "Charlie"],
        })
        data = resp.get_json()
        members = {m["name"]: m["id"] for m in data["members"]}
        return data["id"], members

    def test_create_equal_expense(self, client):
        gid, members = self._create_group(client)

        resp = client.post("/api/expenses", json={
            "description": "Dinner",
            "amount": 90.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "equal",
            "splits": [
                {"member_id": members["Alice"]},
                {"member_id": members["Bob"]},
                {"member_id": members["Charlie"]},
            ],
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["amount"] == 90.0
        assert len(data["splits"]) == 3

    def test_create_percentage_expense(self, client):
        gid, members = self._create_group(client)

        resp = client.post("/api/expenses", json={
            "description": "Hotel",
            "amount": 200.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "percentage",
            "splits": [
                {"member_id": members["Alice"], "percentage": 50.0},
                {"member_id": members["Bob"], "percentage": 30.0},
                {"member_id": members["Charlie"], "percentage": 20.0},
            ],
        })
        assert resp.status_code == 201
        splits = resp.get_json()["splits"]
        assert splits[0]["amount"] == 100.0
        assert splits[1]["amount"] == 60.0
        assert splits[2]["amount"] == 40.0

    def test_rejects_invalid_split_total(self, client):
        gid, members = self._create_group(client)

        resp = client.post("/api/expenses", json={
            "description": "Bad",
            "amount": 100.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "exact",
            "splits": [
                {"member_id": members["Alice"], "amount": 50.0},
                {"member_id": members["Bob"], "amount": 30.0},
            ],
        })
        assert resp.status_code == 422

    def test_rejects_nonmember_payer(self, client):
        gid, members = self._create_group(client)

        resp = client.post("/api/expenses", json={
            "description": "Bad",
            "amount": 100.0,
            "group_id": gid,
            "paid_by": 9999,
            "split_type": "equal",
            "splits": [{"member_id": members["Alice"]}, {"member_id": members["Bob"]}],
        })
        assert resp.status_code == 400

    def test_void_expense(self, client):
        gid, members = self._create_group(client)

        create = client.post("/api/expenses", json={
            "description": "Dinner",
            "amount": 90.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "equal",
            "splits": [
                {"member_id": members["Alice"]},
                {"member_id": members["Bob"]},
                {"member_id": members["Charlie"]},
            ],
        })
        eid = create.get_json()["id"]

        resp = client.post(f"/api/expenses/{eid}/void")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "voided"


class TestBalancesAPI:
    def test_balances_after_expense(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        data = resp.get_json()
        gid = data["id"]
        members = {m["name"]: m["id"] for m in data["members"]}

        client.post("/api/expenses", json={
            "description": "Dinner",
            "amount": 100.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "equal",
            "splits": [
                {"member_id": members["Alice"]},
                {"member_id": members["Bob"]},
            ],
        })

        resp = client.get(f"/api/groups/{gid}/balances")
        assert resp.status_code == 200
        bal_data = resp.get_json()
        assert "balances" in bal_data
        assert "simplified_debts" in bal_data

        balances = {b["member_name"]: b["balance"] for b in bal_data["balances"]}
        assert balances["Alice"] == 50.0
        assert balances["Bob"] == -50.0


class TestSettlementAPI:
    def test_full_settlement_flow(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        data = resp.get_json()
        gid = data["id"]
        members = {m["name"]: m["id"] for m in data["members"]}

        client.post("/api/expenses", json={
            "description": "Dinner",
            "amount": 100.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "equal",
            "splits": [
                {"member_id": members["Alice"]},
                {"member_id": members["Bob"]},
            ],
        })

        resp = client.post("/api/settlements", json={
            "group_id": gid,
            "paid_by": members["Bob"],
            "paid_to": members["Alice"],
            "amount": 50.0,
        })
        assert resp.status_code == 201

        resp = client.get(f"/api/groups/{gid}/balances")
        balances = {b["member_name"]: b["balance"] for b in resp.get_json()["balances"]}
        assert abs(balances["Alice"]) < 0.01
        assert abs(balances["Bob"]) < 0.01

    def test_rejects_self_settlement(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        data = resp.get_json()
        gid = data["id"]
        members = {m["name"]: m["id"] for m in data["members"]}

        resp = client.post("/api/settlements", json={
            "group_id": gid,
            "paid_by": members["Alice"],
            "paid_to": members["Alice"],
            "amount": 10.0,
        })
        assert resp.status_code == 400


class TestActivityAPI:
    def test_activity_recorded_on_group_create(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        gid = resp.get_json()["id"]

        resp = client.get(f"/api/groups/{gid}/activity")
        assert resp.status_code == 200
        activities = resp.get_json()["activities"]
        assert len(activities) >= 1
        assert activities[0]["action"] == "group_created"

    def test_activity_recorded_on_expense(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        data = resp.get_json()
        gid = data["id"]
        members = {m["name"]: m["id"] for m in data["members"]}

        client.post("/api/expenses", json={
            "description": "Dinner",
            "amount": 50.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "equal",
            "splits": [
                {"member_id": members["Alice"]},
                {"member_id": members["Bob"]},
            ],
        })

        resp = client.get(f"/api/groups/{gid}/activity")
        activities = resp.get_json()["activities"]
        actions = [a["action"] for a in activities]
        assert "expense_added" in actions

    def test_activity_recorded_on_settlement(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        data = resp.get_json()
        gid = data["id"]
        members = {m["name"]: m["id"] for m in data["members"]}

        client.post("/api/expenses", json={
            "description": "Dinner",
            "amount": 100.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "equal",
            "splits": [
                {"member_id": members["Alice"]},
                {"member_id": members["Bob"]},
            ],
        })

        client.post("/api/settlements", json={
            "group_id": gid,
            "paid_by": members["Bob"],
            "paid_to": members["Alice"],
            "amount": 50.0,
        })

        resp = client.get(f"/api/groups/{gid}/activity")
        actions = [a["action"] for a in resp.get_json()["activities"]]
        assert "settlement_made" in actions


class TestStatsAPI:
    def test_stats_empty_group(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        gid = resp.get_json()["id"]

        resp = client.get(f"/api/groups/{gid}/stats")
        assert resp.status_code == 200
        stats = resp.get_json()
        assert stats["total_spent"] == 0
        assert stats["expense_count"] == 0

    def test_stats_with_expenses(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        data = resp.get_json()
        gid = data["id"]
        members = {m["name"]: m["id"] for m in data["members"]}

        client.post("/api/expenses", json={
            "description": "Dinner",
            "amount": 100.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "equal",
            "splits": [
                {"member_id": members["Alice"]},
                {"member_id": members["Bob"]},
            ],
        })

        resp = client.get(f"/api/groups/{gid}/stats")
        stats = resp.get_json()
        assert stats["total_spent"] == 100.0
        assert stats["expense_count"] == 1
        assert len(stats["member_spending"]) == 2

    def test_stats_excludes_voided(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        data = resp.get_json()
        gid = data["id"]
        members = {m["name"]: m["id"] for m in data["members"]}

        create = client.post("/api/expenses", json={
            "description": "Dinner",
            "amount": 100.0,
            "group_id": gid,
            "paid_by": members["Alice"],
            "split_type": "equal",
            "splits": [
                {"member_id": members["Alice"]},
                {"member_id": members["Bob"]},
            ],
        })
        eid = create.get_json()["id"]
        client.post(f"/api/expenses/{eid}/void")

        resp = client.get(f"/api/groups/{gid}/stats")
        stats = resp.get_json()
        assert stats["total_spent"] == 0
        assert stats["expense_count"] == 0


class TestAddMemberAPI:
    def test_add_member_to_group(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        gid = resp.get_json()["id"]

        resp = client.post(f"/api/groups/{gid}/members", json={"name": "Charlie"})
        assert resp.status_code == 201
        assert resp.get_json()["name"] == "Charlie"

        resp = client.get(f"/api/groups/{gid}")
        assert len(resp.get_json()["members"]) == 3

    def test_add_member_records_activity(self, client):
        resp = client.post("/api/groups", json={
            "name": "Trip",
            "members": ["Alice", "Bob"],
        })
        gid = resp.get_json()["id"]

        client.post(f"/api/groups/{gid}/members", json={"name": "Charlie"})

        resp = client.get(f"/api/groups/{gid}/activity")
        actions = [a["action"] for a in resp.get_json()["activities"]]
        assert "member_added" in actions
