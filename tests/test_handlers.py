import json
import uuid


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


async def test_get_user_by_id(client, create_user_in_database):
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Lenny",
        "surname": "Kravec",
        "email": "kravec@yandex.ru",
        "is_active": True
    }
    await create_user_in_database(**user_data)
    response = client.get(f"/user/?user_id={user_data['user_id']}")
    print(response)

    assert response.status_code == 200

    user_from_response = response.json()
    assert user_from_response['user_id'] == str(user_data['user_id'])
    assert user_from_response['name'] == user_data['name']
    assert user_from_response['surname'] == user_data['surname']
    assert user_from_response['email'] == user_data['email']
    assert user_from_response['is_active'] == user_data['is_active']


async def test_delete_user_by_id(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Lenny",
        "surname": "Kravec",
        "email": "kravec@yandex.ru",
        "is_active": True
    }

    await create_user_in_database(**user_data)

    response = client.delete(f"/user/?user_id={user_data['user_id']}")
    assert response.status_code == 200
    print(response.json())
    deleted_user_id = response.json()['deleted_user_id']
    assert deleted_user_id == str(user_data['user_id'])

    users_from_db = await get_user_from_database(user_data['user_id'])

    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is False
    assert str(user_from_db["user_id"]) == deleted_user_id
