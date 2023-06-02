import json
import uuid


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

    assert response.status_code == 200

    user_from_response = response.json()
    assert user_from_response['user_id'] == str(user_data['user_id'])
    assert user_from_response['name'] == user_data['name']
    assert user_from_response['surname'] == user_data['surname']
    assert user_from_response['email'] == user_data['email']
    assert user_from_response['is_active'] == user_data['is_active']


async def test_get_user_id_validation_error(client, create_user_in_database):
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Lenny",
        "surname": "Kravec",
        "email": "kravec@yandex.ru",
        "is_active": True
    }
    await create_user_in_database(**user_data)
    response = client.get(f"/user/?user_id=123")
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


async def test_get_user_not_found(client, create_user_in_database):
    user_data = {
        "user_id": uuid.uuid4(),
        "name": "Lenny",
        "surname": "Kravec",
        "email": "kravec@yandex.ru",
        "is_active": True
    }
    user_id_for_finding = uuid.uuid4()
    await create_user_in_database(**user_data)

    response = client.get(f"/user/?user_id={user_id_for_finding}")
    assert response.status_code == 404
    data_from_response = response.json()
    assert data_from_response == {'detail': f'User with id {user_id_for_finding} not found'}
