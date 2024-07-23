import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from api import app

client = TestClient(app)

@pytest.fixture
def mock_records_manager():
    with patch("api.Records_Manager") as mock:
        yield mock

class TestWeatherAPI:

    @pytest.mark.parametrize("endpoint, method_name, sample_data, query_params, expected_status", [
        (
            "/api/weather",
            "fetch_weather_data",
            [{"Station_id": "Station1", "date": "20230101", "max_temperature": 25, "min_temperature": 10, "precipitation": 5}],
            "?date=20230101&station_id=Station1&page=1&per_page=10",
            200
        ),
        (
            "/api/weather/stats",
            "fetch_weather_stats",
            [{"Station_id": "Station1", "avg_max_temperature": 25, "avg_min_temperature": 10, "total_precipitation": 5}],
            "?station_id=Station1",
            200
        ),
        (
            "/api/weather",
            "fetch_weather_data",
            [],
            "?date=invalid_date&station_id=Station1&page=1&per_page=10",
            422
        ),
        (
            "/api/weather",
            "fetch_weather_data",
            [],
            "?date=20230101&station_id=Invalid!@#&page=1&per_page=10",
            422
        ),
        (
            "/api/weather",
            "fetch_weather_data",
            [],
            "?date=20230101&station_id=Station1&page=-1&per_page=10",
            422
        ),
        (
            "/api/weather",
            "fetch_weather_data",
            [],
            "?date=20230101&station_id=Station1&page=1&per_page=101",
            422
        ),
        (
            "/api/weather",
            "fetch_weather_data",
            [],
            "?date=20230101&station_id=Station1&page=9999&per_page=10",
            404
        ),
       
    ])
    def test_api_endpoints(self, mock_records_manager, endpoint, method_name, sample_data, query_params, expected_status):
        # Mock the relevant method of Records_Manager
        getattr(mock_records_manager, method_name).return_value = sample_data

        # Make the API request
        response = client.get(f"{endpoint}{query_params}")

        # Assert the response status code
        assert response.status_code == expected_status

        # If the expected status is 200, check the data
        if expected_status == 200:
            data = response.json()["data"]
            assert len(data) == len(sample_data)
            if sample_data:
                assert data[0] == sample_data[0]

        # Verify that the mocked method was called if status is 200 or 404
        if expected_status in [200, 404]:
            getattr(mock_records_manager, method_name).assert_called_once()
        else:
            getattr(mock_records_manager, method_name).assert_not_called()

if __name__ == "__main__":
    pytest.main(["-v"])
