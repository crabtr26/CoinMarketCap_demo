import json
import os
import time
from datetime import datetime
from json import JSONDecodeError
from typing import Dict, List

from pymongo import MongoClient
from requests import Session
from requests.exceptions import Timeout, TooManyRedirects


class Producer:
    """A pipeline for writing CoinMarketCap data to MongoDB."""

    def __init__(self) -> None:

        connection_string = os.getenv("MONGO_DEMO_CONNECTION_STRING", "")
        if connection_string:
            self.client = MongoClient(connection_string)
            self.collection = self.client["Prices"]["CoinMarketCap"]
        else:
            raise EnvironmentError(
                "Must provide conneciton string using the environment variable MONGO_DEMO_CONNECTION_STRING"
            )

    def start(
        self, start: int = 1, limit: int = 200, currency: str = "USD", sleep: int = 600
    ) -> None:
        """Start the pipeline."""

        while True:
            data = self.fetch_data(start=start, limit=limit, currency=currency)
            if data:
                clean_data = self.process_data(data=data, currency=currency)
                if clean_data:
                    status_code = self.write_data(data=clean_data)
                    if status_code == 0:
                        print(f"Loaded {len(clean_data)} records to MongoDB!")
                    else:
                        print("Error while loading records!")

            time.sleep(sleep)

    def fetch_data(
        self, start: int = 1, limit: int = 200, currency: str = "USD"
    ) -> List[Dict]:
        """Fetch the most recent price data from CoinMarketCap."""

        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

        # Records are returned in a list sorted my market cap
        # start specifies how many records should be skipped
        # limit specifies the total number of records returned
        parameters = {"start": str(start), "limit": str(limit), "convert": currency}
        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": os.getenv("COIN_MARKET_CAP_API_KEY", ""),
        }

        session = Session()
        session.headers.update(headers)

        data = {}
        output = []

        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
        except (JSONDecodeError, Timeout, TooManyRedirects) as e:
            print(e)

        try:
            assert "status" in data
            assert data["status"]["error_code"] == 0
            assert "data" in data
            output = data["data"]
        except AssertionError as e:
            print("Error while fetching data!")
            print(data)
            print(e)

        return output

    def process_data(self, data: List[Dict], currency: str = "USD") -> List[Dict]:
        """Prepare the records to be loaded into MongoDB"""

        clean_data = []

        # Each record should have the schema given by schemas/records_in.json
        for record in data:
            try:
                metadata = {
                    "id": record["id"],
                    "name": record["name"],
                    "symbol": record["symbol"],
                    "slug": record["slug"],
                    "currency": currency,
                }
                fields = {
                    "circulating_supply": record["circulating_supply"],
                    "total_supply": record["total_supply"],
                    "max_supply": record["max_supply"],
                    "price": record["quote"][currency]["price"],
                    "volume_24h": record["quote"][currency]["volume_24h"],
                    "market_cap": record["quote"][currency]["market_cap"],
                    "last_updated": record["quote"][currency]["last_updated"],
                    "timestamp": datetime.utcnow(),
                }

                # Each output document should have the schema given by schemas/records_out.json
                document = {"metadata": metadata}
                document.update(fields)
                clean_data.append(document)
            except KeyError as e:
                print("Could not process record!")
                print(record)
                print(e)

        return clean_data

    def write_data(self, data: List[Dict]) -> int:
        """Upload the records to MongoDB."""

        status_code = 0
        try:
            self.collection.insert_many(data)
        except Exception as e:
            print(e)
            status_code = 1

        return status_code
