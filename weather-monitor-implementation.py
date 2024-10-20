# src/main.py
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List

import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import (
    API_KEY,
    DB_URL,
    CITIES,
    POLLING_INTERVAL,
    TEMPERATURE_THRESHOLD,
    ALERT_WINDOW
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherCollector:
    def __init__(self):
        self.engine = create_async_engine(DB_URL)
        self.SessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.weather_cache: Dict[str, List[dict]] = {city: [] for city in CITIES}
        
    async def fetch_weather(self, city: str) -> dict:
        """Fetch weather data from OpenWeatherMap API."""
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},IN",
            "appid": API_KEY,
            "units": "metric"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self.process_weather_data(data, city)
                else:
                    logger.error(f"Failed to fetch weather for {city}: {response.status}")
                    return None

    def process_weather_data(self, data: dict, city: str) -> dict:
        """Process and standardize weather data."""
        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "condition": data["weather"][0]["main"],
            "timestamp": datetime.fromtimestamp(data["dt"])
        }

    async def store_weather_data(self, data: dict):
        """Store weather data in the database."""
        async with self.SessionLocal() as session:
            weather_record = WeatherData(**data)
            session.add(weather_record)
            await session.commit()

    def calculate_daily_summary(self, city: str) -> dict:
        """Calculate daily weather summary for a city."""
        if not self.weather_cache[city]:
            return None
            
        today_data = [
            record for record in self.weather_cache[city]
            if record["timestamp"].date() == datetime.now().date()
        ]
        
        if not today_data:
            return None
            
        temperatures = [record["temperature"] for record in today_data]
        conditions = [record["condition"] for record in today_data]
        
        return {
            "city": city,
            "date": datetime.now().date(),
            "avg_temp": sum(temperatures) / len(temperatures),
            "max_temp": max(temperatures),
            "min_temp": min(temperatures),
            "dominant_condition": max(set(conditions), key=conditions.count)
        }

    def check_alerts(self, city: str, new_data: dict):
        """Check if any alert conditions are met."""
        recent_records = [
            record for record in self.weather_cache[city]
            if datetime.now() - record["timestamp"] <= ALERT_WINDOW
        ]
        
        if all(record["temperature"] > TEMPERATURE_THRESHOLD for record in recent_records):
            self.trigger_alert(city, "Temperature threshold exceeded")

    def trigger_alert(self, city: str, message: str):
        """Trigger an alert for the specified city."""
        logger.warning(f"ALERT - {city}: {message}")
        # Implementation for email notifications would go here

    async def run_collector(self):
        """Main collection loop."""
        while True:
            tasks = []
            for city in CITIES:
                tasks.append(self.fetch_weather(city))
                
            results = await asyncio.gather(*tasks)
            
            for city, data in zip(CITIES, results):
                if data:
                    await self.store_weather_data(data)
                    self.weather_cache[city].append(data)
                    self.check_alerts(city, data)
                    
                    # Calculate and store daily summary
                    if datetime.now().hour == 23 and datetime.now().minute >= 55:
                        summary = self.calculate_daily_summary(city)
                        if summary:
                            await self.store_daily_summary(summary)
                    
                    # Cleanup old cache entries
                    self.weather_cache[city] = [
                        record for record in self.weather_cache[city]
                        if datetime.now() - record["timestamp"] <= timedelta(days=1)
                    ]
            
            await asyncio.sleep(POLLING_INTERVAL)

if __name__ == "__main__":
    collector = WeatherCollector()
    asyncio.run(collector.run_collector())
