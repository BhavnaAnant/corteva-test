from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
import logging
from api_helper import Records_Manager
from pydantic import BaseModel
from typing import List, Optional
import re

app = FastAPI()

logging.basicConfig(
    filename='logs.log',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

class Validator:
    @staticmethod
    def validate_date(value: str):
        if not re.match(r'^\d{8}$', value):
            raise ValueError('Date must be in YYYYMMDD format')
        return value

    @staticmethod
    def validate_station_id(value: str):
        if not re.match(r'^[A-Za-z0-9]+$', value):
            raise ValueError('Station ID must be alphanumeric and non-empty')
        return value

    @staticmethod
    def validate_pagination(page: int, per_page: int):
        if page < 1:
            raise ValueError('Page number must be greater than 0')
        if per_page < 1 or per_page > 100:
            raise ValueError('Items per page must be between 1 and 100')
        return page, per_page

class WeatherData(BaseModel):
    Station_id: str
    date: str
    max_temperature: Optional[int]
    min_temperature: Optional[int]
    precipitation: Optional[int]

class WeatherStats(BaseModel):
    Station_id: str
    avg_max_temperature: Optional[float]
    avg_min_temperature: Optional[float]
    total_precipitation: Optional[float]

class WeatherDataResponse(BaseModel):
    data: List[WeatherData]

class WeatherStatsResponse(BaseModel):
    data: List[WeatherStats]

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"message": str(exc)},
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"500 Internal Server Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )

@app.get("/api/weather", response_model=WeatherDataResponse)
def get_weather_data(
    date: str = Query(None, title="Date (YYYYMMDD format)"),
    station_id: str = Query(None, title="Station ID"),
    page: int = Query(1, description="Page number"),
    per_page: int = Query(10, description="Items per page"),
):
    """
    Get weather data based on query parameters.
    """
    logger.info(f"Fetching weather data with parameters: date={date}, station_id={station_id}, page={page}, per_page={per_page}")
    try:
        if date:
            Validator.validate_date(date)
        if station_id:
            Validator.validate_station_id(station_id)
        
        # Validate pagination
        page, per_page = Validator.validate_pagination(page, per_page)

        weather_data = Records_Manager.fetch_weather_data(date, station_id, page, per_page)
        
        if not weather_data:
            if station_id:
                # Check if station_id exists
                existing_stations = [record['Station_id'] for record in Records_Manager.fetch_weather_stats()]
                if station_id not in existing_stations:
                    raise HTTPException(status_code=404, detail="Station ID not found.")
            raise HTTPException(status_code=404, detail="No weather data found for the given parameters.")
        return {"data": weather_data}
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException as http_exc:
        logger.error(f"HTTP error fetching weather data: {http_exc}")
        raise
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/api/weather/stats", response_model=WeatherStatsResponse)
def get_weather_stats(
    station_id: str = Query(None, title="Station ID"),
):
    """
    Get weather statistics based on query parameters.
    """
    logger.info(f"Fetching weather statistics with station_id={station_id}")
    try:
        if station_id:
            Validator.validate_station_id(station_id)
            
        weather_stats = Records_Manager.fetch_weather_stats(station_id)
        
        if not weather_stats:
            if station_id:
                # Check if station_id exists
                existing_stations = [record['Station_id'] for record in Records_Manager.fetch_weather_stats()]
                if station_id not in existing_stations:
                    raise HTTPException(status_code=404, detail="Station ID not found.")
            raise HTTPException(status_code=404, detail="No weather statistics found for the given station ID.")
        return {"data": weather_stats}
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except HTTPException as http_exc:
        logger.error(f"HTTP error fetching weather statistics: {http_exc}")
        raise
    except Exception as e:
        logger.error(f"Error fetching weather statistics: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
