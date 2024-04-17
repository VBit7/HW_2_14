# from datetime import date
from unittest.mock import Mock, patch

import pytest

from src.auth.services import auth_service


def test_get_contacts(client, get_token):
    with patch.object(auth_service, 'cache') as redis_mock:
        redis_mock.get.return_value = None
        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/contacts", headers=headers)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 0


# def test_create_contact(client, get_token, monkeypatch):
#     with patch.object(auth_service, 'cache') as redis_mock:
#         redis_mock.get.return_value = None
#         token = get_token
#         headers = {"Authorization": f"Bearer {token}"}
#         response = client.post("api/contacts", headers=headers, json={
#             "first_name": "Jane",
#             "last_name": "Smith",
#             "email": "jane.smith@example.com",
#             "phone_number": "9876543210",
#             "date_of_birth": "1985-08-15",
#             "additional_data": "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
#         })
#         assert response.status_code == 201, response.text
#         data = response.json()
#         assert "id" in data
#         assert data["first_name"] == "Jane"
#         assert data["last_name"] == "Smith"
#         assert data["email"] == "jane.smith@example.com"
#         assert data["phone_number"] == "9876543210"
#         assert data["date_of_birth"] == "1985-08-15"
#         assert data["additional_data"] == "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
