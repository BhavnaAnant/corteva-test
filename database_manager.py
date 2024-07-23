import os
import sqlite3
import logging
from tqdm import tqdm
from datetime import datetime


logger = logging.getLogger("DataBase_Manager")
logging.basicConfig(
    filename='logs.log',
    filemode='a',
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

class DataBase_Manager:
    db_name = 'weather_data.db'
    conn = None
    cursor = None

    @classmethod
    def get_connection(cls):
        if not cls.conn:
            cls.conn = sqlite3.connect(cls.db_name)
            logger.info('Creating connection')
        return cls.conn

    @classmethod
    def get_cursor(cls):
        if not cls.cursor:
            cls.cursor = cls.get_connection().cursor()
        return cls.cursor

    @classmethod
    def close_connection(cls):
        if cls.conn:
            cls.conn.close()
            cls.conn = None
            cls.cursor = None

    @classmethod
    def create_tables(cls):
        cursor = cls.get_cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_data_records (
                Station_id TEXT,
                date TEXT,
                max_temperature INTEGER,
                min_temperature INTEGER,
                precipitation INTEGER,
                PRIMARY KEY (date, Station_id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_data_stats (
                Station_id TEXT PRIMARY KEY,
                avg_max_temperature INTEGER,
                avg_min_temperature INTEGER,
                total_precipitation INTEGER
            )
        """)

    @classmethod
    def ingest_data(cls, file_path):
        start = datetime.now()
        logger.info(f'Data ingestion started at: {start}')

        for file in tqdm(os.listdir(file_path)):
            if file.endswith(".txt"):
                with open(f"{file_path}/{file}") as f:
                    for line in f:
                        record = line.strip().split("\t")
                        record.insert(0, file[:-4])
                        cls.insert_record(record)
        
        cls.clean_data()
        cls.conn.commit()
        
        end = datetime.now()
        logger.info(f'Data ingestion completed at: {end}, total time taken {(end-start).seconds} seconds')

    @classmethod
    def insert_record(cls, record):
        cls.get_cursor().execute(
            "INSERT OR IGNORE INTO weather_data_records (Station_id, date, max_temperature, min_temperature, precipitation) VALUES (?, ?, ?, ?, ?)",
            record
        )

    @classmethod
    def clean_data(cls):
        cls.get_cursor().execute("""
            UPDATE weather_data_records
            SET
                max_temperature = CASE WHEN max_temperature = -9999 THEN 0 ELSE max_temperature END,
                min_temperature = CASE WHEN min_temperature = -9999 THEN 0 ELSE min_temperature END,
                precipitation = CASE WHEN precipitation = -9999 THEN 0 ELSE precipitation END
        """)

    @classmethod
    def calculate_stats(cls):
        cls.get_cursor().execute("""
            INSERT OR REPLACE INTO weather_data_stats (
                Station_id,
                avg_max_temperature,
                avg_min_temperature,
                total_precipitation
            )
            SELECT
                Station_id,
                AVG(CAST(max_temperature AS REAL)) AS average_max_temperature,
                AVG(CAST(min_temperature AS REAL)) AS average_min_temperature,
                SUM(CAST(precipitation AS REAL)) AS total_precipitation
            FROM weather_data_records 
            GROUP BY Station_id
        """)
        cls.get_connection().commit()
if __name__ == "__main__":
    DataBase_Manager.create_tables()
    DataBase_Manager.ingest_data("wx_data")
    DataBase_Manager.calculate_stats()