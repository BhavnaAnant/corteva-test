from database_manager import DataBase_Manager

class Records_Manager:
    @staticmethod
    def fetch_weather_data(date=None, station_id=None, page=1, per_page=10):
        query = "SELECT * FROM weather_data_records WHERE 1=1"
        params = []

        if date:
            query += " AND date = ?"
            params.append(date)
        if station_id:
            query += " AND Station_id = ?"
            params.append(station_id)

        start_index = (page - 1) * per_page
        query += f" LIMIT ? OFFSET ?"
        params.extend([per_page, start_index])

        cursor = DataBase_Manager.get_cursor()
        cursor.execute(query, params)
        data = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in data]
    
    @staticmethod
    def fetch_weather_stats(station_id=None):
        query = "SELECT * FROM weather_data_stats WHERE 1=1"
        params = []

        if station_id:
            query += " AND Station_id = ?"
            params.append(station_id)

        cursor = DataBase_Manager.get_cursor()
        cursor.execute(query, params)
        stats = cursor.fetchall()

        column_names = [description[0] for description in cursor.description]
        return [dict(zip(column_names, row)) for row in stats]