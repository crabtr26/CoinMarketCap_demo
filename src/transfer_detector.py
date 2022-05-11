"""Transfer detector.

Given a list of withdrawals and desposits, detect the likely transfers amongst them.

A few notes:
- The same withdrawal or deposit cannot be used for multiple different transfers.
  If there's a case where a given withdrawal or deposit can be matched with multiple possible transfers,
  use the first occurrence in the list.
- A transfer can only be made between different wallets.

For example, given:
[
	('tx_id_1', 'wallet_id_1', '2020-01-01 15:30:20 UTC', 'out', 5.3),  # 5.3 BTC was withdrawn out of 'wallet_id_1'
	('tx_id_2', 'wallet_id_1', '2020-01-03 12:05:25 UTC', 'out', 3.2),  # 3.2 BTC was withdrawn out of 'wallet_id_1'
	('tx_id_3', 'wallet_id_2', '2020-01-01 15:30:20 UTC', 'in', 5.3),   # 5.3 BTC was deposited into 'wallet_id_2'
	('tx_id_4', 'wallet_id_3', '2020-01-01 15:30:20 UTC', 'in', 5.3),   # 5.3 BTC was deposited into 'wallet_id_3'
]

Expected output:
[
	('tx_id_1', 'tx_id_3'),
]

Add a few tests to verify your implementation works on a variety of input
"""

import pandas as pd


def detect_transfers(transactions):
    """Detects transfers amongst the given transactions."""

    df = pd.DataFrame(
        transactions, columns=["tx_id", "wallet_id", "timestamp", "direction", "amount"]
    )

    # Divide the data into transactions in, and transactions out
    in_df = df[df["direction"] == "in"]
    out_df = df[df["direction"] == "out"]

    # Create a cross product by tx_id to view all potential matches
    matches_df = in_df.merge(out_df, how="cross", suffixes=["_in", "_out"])
    matches_df = matches_df.drop(["direction_in", "direction_out"], axis=1)

    # Potential matches must have the same amount and the same timestamp
    matches_df = matches_df[matches_df["amount_in"] == matches_df["amount_out"]]
    matches_df = matches_df[matches_df["timestamp_in"] == matches_df["timestamp_out"]]

    # Potential matches cannot be between the same wallet_id
    matches_df = matches_df[matches_df["wallet_id_in"] != matches_df["wallet_id_out"]]

    # If there are multiple possible matches, drop all but the first
    first_matches_df = matches_df.drop_duplicates(subset=["tx_id_in"], keep="first")
    first_matches_df = first_matches_df.drop_duplicates(
        subset=["tx_id_out"], keep="first"
    )

    # Make sure no additional matches can be found by matching from the bottom
    last_matches_df = matches_df.drop_duplicates(subset=["tx_id_in"], keep="last")
    last_matches_df = last_matches_df.drop_duplicates(subset=["tx_id_out"], keep="last")

    # If any duplicate matches were found matching from the bottom, remove them.
    final_matches_df = pd.concat([first_matches_df, last_matches_df])
    final_matches_df = final_matches_df.drop_duplicates(
        subset=["tx_id_in"], keep="first"
    )
    final_matches_df = final_matches_df.drop_duplicates(
        subset=["tx_id_out"], keep="first"
    )

    # Convert output datatypes
    output = [
        tuple(record) for record in final_matches_df[["tx_id_out", "tx_id_in"]].values
    ]

    return output
