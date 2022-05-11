# CoinMarketCap_demo
A demo pipeline which consumes cryptocurrency prices using the CoinMarketCap API.

## Description
At a high level, the system is broken into three parts: the producer (python), the database (MongoDB),
and the API (fastapi).

The producer is a pipeline which gathers market data from CoinMarketCap continuously by querying the API
on a fixed interval (default is every ten minutes). The producer then transforms the data into a format
better suited for MongoDB (documents) and removes the unneccessary fields. Each processed document will contain
a metadata sub-document with information about the asset such as the name, symbol, and CoinMarketCap's unique ID.
The remaining fields in the document will be market indicators such as price, volume, and supply.
The market indicators can be quoted in multiple underlying currencies such as USD and EUR,
so the quote currency is also included in a documents metadata. The records consumed from CoinMarketCap have a schema
shown in */src/schemas/records_in.json* and the records produced by the producer and stored in MongoDB have a schema
shown in */src/schemas/records_out.json*

After transforming the data, the producer writes the documents to a MongoDB time series collection. The transformations
applied will ensure good query performance when indexing based on the metadata fields such as name and currency,
as well as good aggregation performance on fields like price, volume, and supply.

Finally, the API serves as the main interface for the application. It gives users a window into the MongoDB database,
as well as access to the transfer detector. There is a single endpoint for exposing the CoinMarketCap data
which includes a number of options. A user can visit the `/data` endpoint to retrieve all of the documents
for all assets. By default, this will retrieve the most recent one hour of documents. If a user would like to lookup
documents during a particular time window, they can provide a *time_start* and *time_stop* using an ISO formatted
timestamp: i.e. `/data?time_start='2022-05-11T00:0:00.000000'&time_stop='2022-05-11T01:0:00.000000'`. If a user is
interested in only a particular asset, they can provide a *symbol* at the endpoint, and optionally specify
the quote *currency*:
i.e. `/data/BTC?currency=USD&time_start='2022-05-11T00:0:00.000000'&time_stop='2022-05-11T01:0:00.000000`.
The transfer detector is also exposed through the API. It can be accessed using:
`/detect_transfers?transactions=[["tx_id_1", "wallet_id_1", "2020-01-01 15:30:20 UTC", "out", 5.3],["tx_id_2", "wallet_id_2", "2020-01-03 12:05:25 UTC", "in", 5.3]]`.


The CLI is included for convenience. It can be used to start the producer and run the transfer detector.

## Setup
```
export MONGO_DEMO_CONNECTION_STRING='mongodb+srv://{}'
export COIN_MARKET_CAP_API_KEY='{}'
conda env create -f environment.yaml
```

## CLI Usage
The CLI features two commands: **produce** to start the CoinMarketCap data pipeline,
and **detect** to run the transfer_detector on a set of test cases, each containing
a different list of transactions.
```
python src/cli.py {produce/detect}
```

For help using the CLI, run the help command:
```
python src/cli.py --help
```

## API Usage
To launch a local API server at http://127.0.0.1:8000:
```
cd src/
uvicorn api:app --reload
```

Autogenerated documentation for the API can be viewed at http://127.0.0.1:8000/docs.
There, you can test the transfer_detector using the payload found in *tests/mock_data*.
You can also view the CoinMarketCap data stored in MongoDB by testing the `/data` and `/data/{symbol}` endpoints.

## Testing
Run the unit tests found in the */test* folder using pytest:
```
pytest
```

## Questions
1. What challenges do you anticipate building and running this system?
  - Reading data continuously from a third party source is always a challenging problem.
    Any unanticipated changes coming from that party can break the assumptions made by your
    system, so it is very important to do extensive error handling, logging, and monitoring.
2. How will you test your system?
  - The code contains some basic unit tests but these should be expanded on. It is important
    to test for unexpected errors while listening for data from CoinMarketCap and to ensure that
    the processed data maintains a consistent schema.
3. How will you monitor system health in production?
  - Many monitoring metrics (cpu/memory utilization, No. connections, etc.) will be included by default
    for the database by using MongoDB Atlas. In addition, many of my "print" statements for debugging
    could be refactored as log messages which can also be easily stored in MongoDB and sent to a
    monitoring service like DataDog or Splunk.

## Deliverables
- Data is captured from the given source every ten minutes.
- Data is stored in MongoDB only after being processed by the producer. It is easy to add additional sanity checks to the
  *producer.process_data()* stage.
- The data can be queried by asset, currency, and timestamp.
- I did not have time to implement the ability to roll back the database to a certain timestamp. However, this should be easy
  to add by building on the API and using the query by timestamp functions.
- The transfer_dector is implemented and passes all of the test cases I have defined. However, I am not 100% confident in my algorithm
  and would like to spend more time testing it.
