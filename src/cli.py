import json
import os
import sys
from pathlib import Path
from pprint import pprint

import typer

sys.path.append(str(Path(__file__).parent.parent))
from src.producer import Producer
from src.transfer_detector import detect_transfers

app = typer.Typer()


@app.command()
def produce(
    start: int = 1, limit: int = 200, currency: str = "USD", sleep: int = 600
) -> None:
    "Start producing data from CoinMarketCap."

    producer = Producer()
    producer.start(start=start, limit=limit, currency=currency, sleep=sleep)


@app.command()
def detect(file: str) -> None:
    "Detect transfers amongst the given transactions."

    fpath = os.path.join(os.getcwd(), file)
    with open(fpath, "r", encoding="UTF-8") as f:
        all_transactions = json.loads(f.read())

    for case in all_transactions["cases"]:
        transactions = [tuple(transaction) for transaction in case["transactions"]]
        print("#" * 100, "\n")
        print("Transactions:")
        pprint(transactions)
        print("\n")
        transfers = detect_transfers(transactions=transactions)
        print("Transfers")
        print(transfers, "\n")
    print("#" * 100)


if __name__ == "__main__":
    app()
