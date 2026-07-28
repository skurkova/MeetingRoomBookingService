import pytest
from httpx import AsyncClient

TEST_BOOKING_DATE = "2026-07-15"
TEST_BOOKING_DATAS = {"room_slot_id": 1, "booking_date": TEST_BOOKING_DATE}


class TestBooking:

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method, url",
        [
            ("GET", "/bookings/"),
            ("POST", "/bookings/"),
            ("GET", "/bookings/1"),
            ("DELETE", "/bookings/1"),
        ],
    )
    async def test_booking_unauthorized_user(
        self, client: AsyncClient, method: str, url: str
    ):
        """Тест проверки отсутствия аутентификации для роутов бронирования"""

        request_func = getattr(client, method.lower())
        if method == "POST":
            response = await request_func(url=url, json=TEST_BOOKING_DATAS)
        else:
            response = await request_func(url=url)

        response_data = response.json()

        assert response.status_code == 401
        assert response_data["detail"] == "Not authenticated"
        assert response.headers.get("WWW-Authenticate") == "Bearer"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "method, url, expected_status",
        [
            ("GET", "/bookings/", 200),
            ("POST", "/bookings/", 201),
        ],
    )
    async def test_booking_authorized_user(
        self,
        client: AsyncClient,
        method: str,
        url: str,
        expected_status: int,
        headers_employee_auth: dict,
    ):
        """Тест проверки аутентификации для роутов бронирования"""

        request_func = getattr(client, method.lower())
        if method == "POST":
            response = await request_func(
                url=url, json=TEST_BOOKING_DATAS, headers=headers_employee_auth
            )
        else:
            response = await request_func(url=url, headers=headers_employee_auth)

        assert response.status_code == expected_status

    @pytest.mark.asyncio
    async def test_get_all_bookings_for_admin(
        self, client: AsyncClient, headers_admin_auth: dict
    ):
        """Тест проверки получения всех бронирований админом"""

        await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_admin_auth
        )

        response = await client.get(url="/bookings/", headers=headers_admin_auth)
        response_data = response.json()

        assert response.status_code == 200
        assert isinstance(response_data, list)
        assert len(response_data) > 0

    @pytest.mark.asyncio
    async def test_get_all_bookings_for_employee(
        self, client: AsyncClient, headers_admin_auth: dict, headers_employee_auth: dict
    ):
        """Тест проверки получения всех бронирований сотрудником"""

        await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_admin_auth
        )

        response = await client.get(url="/bookings/", headers=headers_employee_auth)
        response_data = response.json()

        assert response.status_code == 200
        assert isinstance(response_data, list)
        assert response_data == []

    @pytest.mark.asyncio
    async def test_get_bookings_not_found(
        self, client: AsyncClient, headers_employee_auth: dict
    ):
        """Тест проверки отсутствия бронирований"""

        response = await client.get(url="/bookings/", headers=headers_employee_auth)
        response_data = response.json()

        assert response.status_code == 200
        assert response_data == []

    @pytest.mark.asyncio
    async def test_create_booking_for_admin(
        self, client: AsyncClient, headers_admin_auth: dict
    ):
        """Тест проверки создания бронирования администратором"""

        response = await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_admin_auth
        )
        response_data = response.json()

        assert response.status_code == 201
        assert "id" in response_data
        assert response_data.get("booking_date") == TEST_BOOKING_DATE
        assert response_data["room_slot"]["id"] == TEST_BOOKING_DATAS["room_slot_id"]

    @pytest.mark.asyncio
    async def test_create_booking_for_employee(
        self, client: AsyncClient, headers_employee_auth: dict
    ):
        """Тест проверки создания бронирования сотрудником"""

        response = await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_employee_auth
        )
        response_data = response.json()

        assert response.status_code == 201
        assert "id" in response_data
        assert response_data.get("booking_date") == TEST_BOOKING_DATE
        assert response_data["room_slot"]["id"] == TEST_BOOKING_DATAS["room_slot_id"]

    @pytest.mark.asyncio
    async def test_create_exist_booking(
        self, client: AsyncClient, headers_admin_auth: dict, headers_employee_auth: dict
    ):
        """Тест проверки создания повторного бронирования"""

        await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_admin_auth
        )

        response_error = await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_employee_auth
        )
        response_error_data = response_error.json()

        assert response_error.status_code == 409
        assert (
            response_error_data.get("detail")
            == "Room is already for this datetime booking"
        )

    @pytest.mark.asyncio
    async def test_create_unauthorized_user(self, client: AsyncClient):
        """
        Тест проверки невозможности создания бронирования
        неавторизированным пользователем
        """

        response_error = await client.post(url="/bookings/", json=TEST_BOOKING_DATAS)
        response_error_data = response_error.json()

        assert response_error.status_code == 401
        assert response_error_data.get("detail") == "Not authenticated"

    @pytest.mark.asyncio
    async def test_get_booking_id(
        self, client: AsyncClient, headers_admin_auth: dict, headers_employee_auth: dict
    ):
        """Тест проверки получения бронирования по ID"""

        response_create = await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_employee_auth
        )
        response_create_data = response_create.json()

        booking_id = response_create_data["id"]
        response = await client.get(
            url=f"/bookings/{booking_id}", headers=headers_admin_auth
        )
        response_data = response.json()

        assert response.status_code == 200
        assert isinstance(response_data.get("id"), int)

    @pytest.mark.asyncio
    async def test_get_booking_id_forbidden(
        self, client: AsyncClient, headers_admin_auth: dict, headers_employee_auth: dict
    ):
        """Тест отсутствия доступа для получения чужого бронирования по ID"""

        response_create = await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_admin_auth
        )
        response_create_data = response_create.json()

        booking_id = response_create_data["id"]
        response = await client.get(
            url=f"/bookings/{booking_id}", headers=headers_employee_auth
        )
        response_data = response.json()

        assert response.status_code == 403
        assert response_data["detail"] == "FORBIDDEN for this user"

    @pytest.mark.asyncio
    async def test_get_booking_id_unauthorized_user(
        self, client: AsyncClient, headers_admin_auth: dict
    ):
        """
        Тест отсутствия доступа для получения бронирования
        по ID неавторизированным пользователем
        """

        response_create = await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_admin_auth
        )
        response_create_data = response_create.json()

        booking_id = response_create_data["id"]
        response = await client.get(url=f"/bookings/{booking_id}")
        response_data = response.json()

        assert response.status_code == 401
        assert response_data.get("detail") == "Not authenticated"

    @pytest.mark.asyncio
    async def test_get_booking_not_found(
        self, client: AsyncClient, headers_admin_auth: dict
    ):
        """Тест получения отсутствующего бронирования"""

        response = await client.get("/bookings/1", headers=headers_admin_auth)
        response_data = response.json()

        assert response.status_code == 404
        assert response_data["detail"] == "Booking not found"

    @pytest.mark.asyncio
    async def test_delete_booking_id(
        self, client: AsyncClient, headers_admin_auth: dict, headers_employee_auth: dict
    ):
        """Тест проверки удаления бронирования по ID"""

        response_create = await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_employee_auth
        )
        response_create_data = response_create.json()

        booking_id = response_create_data["id"]
        response = await client.delete(
            url=f"/bookings/{booking_id}", headers=headers_admin_auth
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_booking_id_forbidden(
        self, client: AsyncClient, headers_admin_auth: dict, headers_employee_auth: dict
    ):
        """Тест проверки запрещающий удаление чужого бронирования по ID"""

        response_create = await client.post(
            url="/bookings/", json=TEST_BOOKING_DATAS, headers=headers_admin_auth
        )
        response_create_data = response_create.json()

        booking_id = response_create_data["id"]
        response = await client.delete(
            url=f"/bookings/{booking_id}", headers=headers_employee_auth
        )
        response_data = response.json()

        assert response.status_code == 403
        assert response_data.get("detail") == "FORBIDDEN for this user"

    @pytest.mark.asyncio
    async def test_delete_booking_not_found(
        self, client: AsyncClient, headers_employee_auth: dict
    ):
        """Тест проверки удаления несуществующего бронирования"""

        response = await client.delete(url="/bookings/1", headers=headers_employee_auth)
        response_data = response.json()

        assert response.status_code == 404
        assert response_data.get("detail") == "Booking not found"
