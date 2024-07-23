import pytest
import sqlite3
from database_manager import DataBase_Manager

@pytest.fixture(scope="module")
def test_db():
    original_db_name = DataBase_Manager.db_name
    DataBase_Manager.db_name = ":memory:"
    DataBase_Manager.create_tables()
    yield
    DataBase_Manager.close_connection()
    DataBase_Manager.db_name = original_db_name

@pytest.fixture
def sample_record():
    return ("Station1", "2023-01-01", 25, 10, 5)

class TestDataBaseManager:

    def test_connection(self, test_db):
        assert isinstance(DataBase_Manager.get_connection(), sqlite3.Connection)

    def test_table_creation(self, test_db):
        cursor = DataBase_Manager.get_cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = {table[0] for table in cursor.fetchall()}
        assert "weather_data_records" in tables
        assert "weather_data_stats" in tables

    def test_data_ingestion(self, test_db, sample_record):
        DataBase_Manager.insert_record(sample_record)
        cursor = DataBase_Manager.get_cursor()
        cursor.execute("SELECT * FROM weather_data_records WHERE Station_id = ?;", (sample_record[0],))
        data = cursor.fetchone()
        assert data == sample_record

    def test_data_analysis(self, test_db, sample_record):
        DataBase_Manager.insert_record(sample_record)
        DataBase_Manager.calculate_stats()
        cursor = DataBase_Manager.get_cursor()
        cursor.execute("SELECT * FROM weather_data_stats WHERE Station_id = ?;", (sample_record[0],))
        data = cursor.fetchone()
        assert data is not None
        avg_max_temp, avg_min_temp, total_precip = data[1:4]
        assert 20 <= avg_max_temp <= 30
        assert 5 <= avg_min_temp <= 15
        assert 0 <= total_precip <= 10

    def test_data_redundancy(self, test_db):
        redundant_record = ("Station2", "2023-01-01", 25, 10, 5)
        DataBase_Manager.insert_record(redundant_record)
        DataBase_Manager.insert_record(redundant_record)
        cursor = DataBase_Manager.get_cursor()
        cursor.execute("SELECT COUNT(*) FROM weather_data_records WHERE Station_id = ?;", (redundant_record[0],))
        count = cursor.fetchone()[0]
        assert count == 1

if __name__ == "__main__":
    pytest.main(["-v"])