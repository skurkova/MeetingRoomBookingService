import pytest

from httpx import AsyncClient


class TestAuth:
    """Тесты для роута аутентификации"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_data, expected_status, expected_detail", [
        ({"username": "admin", "password": "admin123"}, 200, "access_token"),
        ({"username": "employee_1", "password": "employee1_123"}, 200, "access_token"),
        ({"username": "employee", "password": "employee"}, 401, "Incorrect username or password"),
    ])
    async def test_login_status_code(self,
                                     client: AsyncClient,
                                     user_data: dict,
                                     expected_status: int,
                                     expected_detail: str):
        """Тест проверки статуса кода входа в систему"""

        response = await client.post(url="/auth/login", data=user_data)
        response_data = response.json()

        assert response.status_code == expected_status
        if response.status_code == 200:
            assert expected_detail in response_data
            assert response_data["token_type"] == "bearer"
        else:
            assert response_data.get("detail") == expected_detail
