import json
import uuid
import pytest


async def test_create_user(client, get_user_from_database):
    user_data = {
        "name": "Lenny",
        "surname": "Kravec",
        "email": "kravec@yandex.ru"
    }
    resp = client.post("/user/", data=json.dumps(user_data))
    data_from_resp = resp.json()

    assert resp.status_code == 200
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True

    users_from_db = await get_user_from_database(data_from_resp["user_id"])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert str(user_from_db["user_id"]) == data_from_resp["user_id"]


async def test_create_user_duplicate_email_error(client, get_user_from_database):
    user_data = {
        "name": "Lenny",
        "surname": "Kravitz",
        "email": "kravec@yandex.ru"
    }

    user_data_same_email = {
        "name": "John",
        "surname": "Snow",
        "email": "kravec@yandex.ru"
    }

    response = client.post("/user/", data=json.dumps(user_data))
    data_from_resp = response.json()

    assert response.status_code == 200
    assert data_from_resp["name"] == user_data["name"]
    assert data_from_resp["surname"] == user_data["surname"]
    assert data_from_resp["email"] == user_data["email"]
    assert data_from_resp["is_active"] is True

    users_from_db = await get_user_from_database(data_from_resp['user_id'])
    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert response.status_code == 200
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is True
    assert data_from_resp["user_id"] == str(user_from_db["user_id"])

    response = client.post("/user/", data=json.dumps(user_data_same_email))
    assert response.status_code == 503
    assert 'duplicate key value violates unique constraint "users_email_key"' in response.json()["detail"]


@pytest.mark.parametrize(
    "user_data_for_creation, expected_status_code, expected_detail",
    [
        (
            {},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "name"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["body", "surname"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                    {
                        "loc": ["body", "email"],
                        "msg": "field required",
                        "type": "value_error.missing",
                    },
                ]
            },
        ),
        (
            {"name": 123, "surname": 456, "email": "lol"},
            422,
            {"detail": "Name should contains only letters"},
        ),
        (
            {"name": "Nikolai", "surname": 456, "email": "lol"},
            422,
            {"detail": "Surname should contains only letters"},
        ),
        (
            {"name": "Nikolai", "surname": "Sviridov", "email": "lol"},
            422,
            {
                "detail": [
                    {
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                        "type": "value_error.email",
                    }
                ]
            },
        ),
    ],
)
async def test_create_validation_error(client, user_data_for_creation,
                                       expected_status_code, expected_detail):
    response = client.post("/user/", data=json.dumps(user_data_for_creation))
    data_from_response = response.json()
    assert response.status_code == expected_status_code
    assert data_from_response == expected_detail
