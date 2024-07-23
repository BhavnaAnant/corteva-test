# Coding Challenge : Weather Stats

This is a Weather API based on FastAPI, designed to deliver weather information to users.

The API comprises the following endpoints, each serving distinct purposes:

/api/weather: Allows users to retrieve weather data.

/api/weather/stats: Offers statistical insights into the available weather data.

# Installation

First we need to have python (3.7 and above).
Then we need to create a virtual environment.

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment (Mac)
source venv/bin/activate

# Activate the virtual environment (Windows)
venv\Scripts\activate
```

We need to have necessary dependencies from requirements.txt using virtual environment.

```bash
pip3 install -r requirements.txt
```

The python3 database_manager.py generates a weather_data.db file.

```bash
python3 database_manager.py
```

Use the below command to run the FastAPI server on port 8000.

```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

## Endpoints

For /api/weather :

```bash
http://localhost:8000/docs
#/default/get_weather_data_api_weather_get
```

For /api/weather/stats :

```bash
http://localhost:8000/docs
#/default/get_weather_stats_api_weather_stats_get
```

# Testing

For testing purpose of the APIs, for the files, test_api.py, test_database_manager.py and test_api_helper.py use pytest command on terminal to check the results

```bash
pytest
```

# AWS Deployment

For deployment on AWS, I'll prefer to use below serives:

- ### Database:

    RDS (Relational Database Service): To host our relational database with support for engines like PostgreSQL or MySQL.

- ### API
    Elastic Beanstalk: Ideal for deploying web applications, particularly those using frameworks such as FastAPI, Flask, or Django.

- ### Data Ingestion:
    AWS Lambda: For handling the data ingestion process, with the ability to schedule these tasks.

- ### Static Data Storage:

    Amazon S3: For storing weather data files, offering scalable, durable, and efficient storage and retrieval.

- ### Swagger Documentation:
    Hosting Swagger documentation on an S3 bucket or using API Gateway to manage it.

- ### API Gateway:
    Amazon API Gateway: To manage REST API endpoints, enabling easy creation and publishing of APIs.


## Output Screenshots
![Screenshot1](screenshot/Screenshot1.png)
![Screenshot2](screenshot/Screenshot2.png)


