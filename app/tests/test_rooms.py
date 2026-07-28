import pytest
from httpx import AsyncClient


class TestRooms:
    """Тесты для роута переговорных комнат"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("url", ["/rooms/", "/rooms/?target_date=2026-07-15"])
    async def test_get_all_rooms(self, client: AsyncClient, url: str):
        """Тест проверки получения всех комнат"""

        response = await client.get(url=url)
        response_data = response.json()

        assert response.status_code == 200
        assert isinstance(response_data, list)
        assert len(response_data) > 0
        assert "id" and "room_slots" in response_data[0]
        assert (
            "room_id"
            and "time_slot"
            and "is_available" in response_data[0]["room_slots"][0]
        )
        assert (
            "id"
            and "start_time"
            and "end_time" in response_data[0]["room_slots"][0]["time_slot"]
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "url, expected_status",
        [
            ("/rooms/1", 200),
            ("/rooms/1?target_date=2026-07-15", 200),
            ("/rooms/4?target_date=2026-07-25", 404),
        ],
    )
    async def test_get_room_id(self, client: AsyncClient, url: str, expected_status):
        """Тест проверки получения комнаты по ID"""

        response = await client.get(url=url)
        response_data = response.json()

        assert response.status_code == expected_status
        if response.status_code == 200:
            assert response_data.get("id") == 1
            assert "room_slots" in response_data
            assert (
                "room_id"
                and "time_slot"
                and "is_available" in response_data["room_slots"][0]
            )
            assert (
                "id"
                and "start_time"
                and "end_time" in response_data["room_slots"][0]["time_slot"]
            )
        else:
            assert response_data.get("detail") == "Room not found"
