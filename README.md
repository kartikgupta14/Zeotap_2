# Real-Time Weather Monitoring System

A Python-based real-time weather monitoring system that collects, processes, and analyzes weather data from OpenWeatherMap API for major Indian metros.

## Features

- Real-time weather data collection for 6 major Indian metros
- Temperature conversion and standardization
- Daily weather summaries and aggregates
- Configurable alerting system
- Data visualization dashboard
- Historical data storage and analysis

## Architecture

```
weather-monitor/
├── src/
│   ├── collectors/         # Data collection modules
│   ├── processors/        # Data processing logic
│   ├── storage/          # Database interactions
│   ├── visualization/    # Dashboard and charts
│   └── alerts/           # Alerting system
├── tests/                # Test cases
├── config/              # Configuration files
└── docker/             # Docker configurations
```

## Prerequisites

- Python 3.9+
- Docker or Podman
- OpenWeatherMap API key

## Dependencies

```
python-packages:
  - fastapi==0.104.1
  - sqlalchemy==2.0.23
  - pandas==2.1.3
  - plotly==5.18.0
  - requests==2.31.0
  - pytest==7.4.3

containers:
  - postgres:15-alpine
  - grafana/grafana:latest
```

## Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/kartikgupta14/weather-monitor.git
cd weather-monitor
```

2. Create a `.env` file:
```bash
OPENWEATHERMAP_API_KEY=your_api_key_here
DB_HOST=localhost
DB_PORT=5432
DB_NAME=weather_db
DB_USER=weather_user
DB_PASSWORD=your_password
```

3. Start the containers:
```bash
docker-compose up -d
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Initialize the database:
```bash
python src/storage/init_db.py
```

## Running the Application

1. Start the data collector:
```bash
python src/main.py collector
```

2. Start the web dashboard:
```bash
python src/main.py dashboard
```

Access the dashboard at `http://localhost:8000`

## Testing

Run the test suite:
```bash
pytest tests/
```

## Design Choices

1. **Data Collection Strategy**:
   - Implemented parallel collectors for each city using asyncio
   - Configurable polling intervals with exponential backoff
   - Bulk inserts for better database performance

2. **Storage**:
   - PostgreSQL for structured data storage
   - TimescaleDB extension for efficient time-series operations
   - Partitioning by city and date for query optimization

3. **Alerting System**:
   - In-memory state management for real-time threshold monitoring
   - Configurable alert conditions using JSON-based rules
   - Email notifications via SMTP with retry mechanism

4. **Visualization**:
   - Grafana dashboards for real-time monitoring
   - Plotly for interactive charts
   - Data aggregation at multiple time granularities

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details
