import pytest
from api_helper import Records_Manager
from database_manager import DataBase_Manager

TEST_DB_NAME = "test_weather_data.db"

@pytest.fixture(scope="module")
def test_db():
    original_db_name = DataBase_Manager.db_name
    DataBase_Manager.db_name = TEST_DB_NAME
    DataBase_Manager.create_tables()
    yield
    DataBase_Manager.close_connection()
    import os
    os.remove(TEST_DB_NAME)
    DataBase_Manager.db_name = original_db_name

@pytest.fixture(scope="function")
def sample_weather_data():
    return {
        "Station_id": "Station1",
        "date": "20230101",
        "max_temperature": 25,
        "min_temperature": 10,
        "precipitation": 5,
    }

@pytest.fixture(scope="function")
def sample_weather_stats():
    return {
        "Station_id": "Station1",
        "avg_max_temperature": 25,
        "avg_min_temperature": 10,
        "total_precipitation": 5,
    }

class TestRecordsManager:

    def test_fetch_weather_data(self, test_db, sample_weather_data):
        # Insert sample data
        DataBase_Manager.insert_record([
            sample_weather_data["Station_id"],
            sample_weather_data["date"],
            sample_weather_data["max_temperature"],
            sample_weather_data["min_temperature"],
            sample_weather_data["precipitation"]
        ])
        DataBase_Manager.get_connection().commit()

        # Fetch and verify data
        data = Records_Manager.fetch_weather_data(
            date=sample_weather_data["date"],
            station_id=sample_weather_data["Station_id"]
        )
        assert len(data) == 1
        assert data[0] == sample_weather_data

    def test_fetch_weather_data_invalid_station_id(self, test_db):
        # Fetch data with invalid station_id
        data = Records_Manager.fetch_weather_data(
            date="20230101",
            station_id="InvalidStation"
        )
        assert data == []

    def test_fetch_weather_data_invalid_date(self, test_db):
        # Fetch data with invalid date format
        data = Records_Manager.fetch_weather_data(
            date="invalid_date",
            station_id="Station1"
        )
        assert data == []

    def test_fetch_weather_stats(self, test_db, sample_weather_stats):
        # Insert sample stats
        cursor = DataBase_Manager.get_cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO weather_data_stats 
            (Station_id, avg_max_temperature, avg_min_temperature, total_precipitation) 
            VALUES (?, ?, ?, ?)
        """, (
            sample_weather_stats["Station_id"],
            sample_weather_stats["avg_max_temperature"],
            sample_weather_stats["avg_min_temperature"],
            sample_weather_stats["total_precipitation"]
        ))
        DataBase_Manager.get_connection().commit()

        # Fetch and verify stats
        stats = Records_Manager.fetch_weather_stats(station_id=sample_weather_stats["Station_id"])
        assert len(stats) == 1
        assert stats[0] == sample_weather_stats

    def test_fetch_weather_stats_invalid_station_id(self, test_db):
        # Fetch stats with invalid station_id
        stats = Records_Manager.fetch_weather_stats(station_id="InvalidStation")
        assert stats == []

if __name__ == "__main__":
    pytest.main(["-v"])
