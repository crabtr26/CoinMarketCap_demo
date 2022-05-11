import asyncio
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from fastapi import FastAPI
from motor import motor_asyncio

sys.path.append(str(Path(__file__).parent.parent))
from src.transfer_detector import detect_transfers

app = FastAPI()
CLIENT = None
COLLECTION = None


@app.get("/")
async def root():
    return "Hello CoinTracker!"


@app.on_event("startup")
async def connect_mongo():
    """Setup a connection to the MongoDB collection."""

    global CLIENT
    global COLLECTION
    connection_string = os.getenv("MONGO_DEMO_CONNECTION_STRING", "")
    if connection_string:
        CLIENT = motor_asyncio.AsyncIOMotorClient(connection_string)
        CLIENT.get_io_loop = asyncio.get_running_loop
        COLLECTION = CLIENT["Prices"]["CoinMarketCap"]
    else:
        raise EnvironmentError(
            "Must provide conneciton string using the environment variable MONGO_DEMO_CONNECTION_STRING"
        )


@app.get("/data")
async def fetch_all_prices(
    time_start: str = (datetime.utcnow() - timedelta(hours=1)).isoformat(),
    time_stop: str = datetime.utcnow().isoformat(),
):
    """Return CoinMarketCap data for all assets within the given timestamps."""

    time_start = pd.to_datetime(time_start)
    time_stop = pd.to_datetime(time_stop)

    documents = []
    if COLLECTION is not None:
        cursor = COLLECTION.find(
            {"timestamp": {"$gte": time_start, "$lte": time_stop}},
            projection={"_id": 0},
        )
        async for document in cursor:
            documents.append(document)

    return documents


@app.get("/data/{symbol}")
async def fetch_prices(
    symbol: str,
    currency: str = "USD",
    time_start: str = (datetime.utcnow() - timedelta(hours=1)).isoformat(),
    time_stop: str = datetime.utcnow().isoformat(),
):
    """Return CoinMarketCap data for the selected asset within the given timestamps."""

    time_start = pd.to_datetime(time_start)
    time_stop = pd.to_datetime(time_stop)

    documents = []
    if COLLECTION is not None:
        cursor = COLLECTION.find(
            {
                "metadata.symbol": symbol,
                "metadata.currency": currency,
                "timestamp": {"$gte": time_start, "$lte": time_stop},
            },
            projection={"_id": 0},
        )
        async for document in cursor:
            documents.append(document)

    return documents


@app.post("/detect_transfers")
async def handle_transactions(transactions: List[Tuple]):
    """Detect transfers amongst the given transactions."""

    transfers = detect_transfers(transactions)
    return transfers
