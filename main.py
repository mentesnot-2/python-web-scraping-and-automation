import aiohttp
import asyncio
import requests
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CryptoScraper:
    """Handles cryptocurrency data scraping and fetching."""
    
    COINMARKETCAP_URL = 'https://coinmarketcap.com/'

    @staticmethod
    async def fetch_crypto_prices() -> List[Dict[str, Any]]:
        """Fetch current cryptocurrency prices asynchronously."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(CryptoScraper.COINMARKETCAP_URL) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Example of extracting the top 5 cryptocurrencies
                    crypto_prices = []
                    table_rows = soup.find_all('tr')[:5]
                    for row in table_rows:
                        cols = row.find_all('td')
                        if len(cols) > 0:
                            name = cols[2].find('a').text if cols[2].find('a') else 'N/A'
                            price = cols[3].find('a').text if cols[3].find('a') else 'N/A'
                            crypto_prices.append({'name': name, 'price': price})

                    logger.info("Fetched crypto prices successfully.")
                    return crypto_prices
        except Exception as e:
            logger.error(f"Error fetching crypto prices: {e}")
            return []

    @staticmethod
    def fetch_crypto_news() -> List[str]:
        """Fetch cryptocurrency news."""
        news_url = 'https://cryptonews.com/'
        try:
            response = requests.get(news_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            headlines = [headline.text.strip() for headline in soup.find_all('h4')[:5]]  # Get top 5 news
            logger.info("Fetched crypto news successfully.")
            return headlines
        except Exception as e:
            logger.error(f"Error fetching crypto news: {e}")
            return []

class NewsScraper:
    """Handles news scraping for various topics."""

    NEWS_API_URL = 'https://newsapi.org/v2/everything'
    API_KEY = 'bec47ecaa8284585b971192be77b8312'

    @staticmethod
    async def get_latest_news(topic: str = 'technology', lang_code: str = 'en') -> List[Dict[str, Any]]:
        """Fetch latest news articles asynchronously."""
        params = {
            'q': topic,
            'language': lang_code,
            'apiKey': NewsScraper.API_KEY,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(NewsScraper.NEWS_API_URL, params=params) as response:
                    data = await response.json()
                    articles = data.get('articles', [])[:5]  # Get top 5 articles
                    logger.info(f"Fetched {len(articles)} news articles for topic '{topic}'.")
                    return articles
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return []

class WeatherScraper:
    """Handles weather data scraping."""

    WEATHER_API_URL = 'https://api.openweathermap.org/data/2.5/weather'
    API_KEY = '59362194dc9f35a6552480d56ffb1a92'

    @staticmethod
    async def get_latest_weather(location: str = 'Addis Ababa') -> Dict[str, Any]:
        """Fetch latest weather data asynchronously."""
        params = {
            'q': location,
            'appid': WeatherScraper.API_KEY,
            'units': 'metric'
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(WeatherScraper.WEATHER_API_URL, params=params) as response:
                    data = await response.json()
                    if response.status == 200:
                        logger.info(f"Fetched weather data for {location} successfully.")
                        return data
                    else:
                        logger.error(f"Failed to fetch weather data: {data.get('message')}")
                        return {}
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return {}

class AutomationScraper:
    """Main class to coordinate different scraping functionalities."""

    def __init__(self):
        self.crypto_scraper = CryptoScraper()
        self.news_scraper = NewsScraper()
        self.weather_scraper = WeatherScraper()

    async def fetch_all_data(self, topic: str = 'technology', location: str = 'Addis Ababa') -> Dict[str, Any]:
        """Fetch all data asynchronously."""
        crypto_prices_task = self.crypto_scraper.fetch_crypto_prices()
        news_task = self.news_scraper.get_latest_news(topic)
        weather_task = self.weather_scraper.get_latest_weather(location)

        crypto_prices, news_articles, weather_data = await asyncio.gather(
            crypto_prices_task, news_task, weather_task
        )

        return {
            'crypto_prices': crypto_prices,
            'news_articles': news_articles,
            'weather_data': weather_data
        }

def run_automation_scraper():
    """Command-line interface for interacting with the scraper."""
    print("Welcome to the Automation Scraper!")
    print("Select an option:")
    print("1. Fetch Cryptocurrency Data")
    print("2. Fetch Latest News")
    print("3. Fetch Weather Data")

    try:
        option = int(input("Enter your choice (1-3): "))
    except ValueError:
        print("Invalid input. Please enter a number between 1 and 3.")
        return

    scraper = AutomationScraper()

    if option == 1:
        loop = asyncio.get_event_loop()
        crypto_prices = loop.run_until_complete(scraper.crypto_scraper.fetch_crypto_prices())
        print("\n--- Cryptocurrency Prices ---")
        for crypto in crypto_prices:
            print(f"{crypto['name']}: {crypto['price']}")
    
    elif option == 2:
        topic = input("Enter the news topic (e.g., technology, sports): ")
        loop = asyncio.get_event_loop()
        news_articles = loop.run_until_complete(scraper.news_scraper.get_latest_news(topic))
        print(f"\n--- Latest News on {topic} ---")
        for article in news_articles:
            print(f"{article['title']} - {article['source']['name']}")
    
    elif option == 3:
        location = input("Enter the location for weather (e.g., Addis Ababa): ")
        loop = asyncio.get_event_loop()
        weather_data = loop.run_until_complete(scraper.weather_scraper.get_latest_weather(location))
        print(f"\n--- Weather Data for {location} ---")
        print(weather_data)
    
    else:
        print("Invalid option. Please select 1, 2, or 3.")

# Entry point for the script
if __name__ == "__main__":
    run_automation_scraper()
