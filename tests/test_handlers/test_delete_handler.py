import uuid


async def test_delete_user_by_id(
    client, create_user_in_database, get_user_from_database
):
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Lenny",
        "surname": "Kravec",
        "email": "kravec@yandex.ru",
        "is_active": True,
    }

    await create_user_in_database(**user_data)

    response = client.delete(f"/user/?user_id={user_data['user_id']}")
    assert response.status_code == 200
    print(response.json())
    deleted_user_id = response.json()["deleted_user_id"]
    assert deleted_user_id == str(user_data["user_id"])

    users_from_db = await get_user_from_database(user_data["user_id"])

    assert len(users_from_db) == 1
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is False
    assert str(user_from_db["user_id"]) == deleted_user_id


async def test_delete_user_not_found(client):
    user_id = uuid.uuid4()
    response = client.delete(f"/user/?user_id={user_id}")
    assert response.status_code == 404
    assert response.json() == {"detail": f"user with id {user_id} not found"}


async def test_delete_user_user_id_validation_error(client):
    response = client.delete("/user/?user_id=123")
    assert response.status_code == 422
    data_from_response = response.json()
    assert data_from_response == {
        "detail": [
            {
                "loc": ["query", "user_id"],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }
