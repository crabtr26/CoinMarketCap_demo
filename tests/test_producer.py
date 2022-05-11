import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from src.producer import Producer


def test_producer():
    producer = Producer()
    data = producer.fetch_data(limit=100)
    assert len(data) == 100
    clean_data = producer.process_data(data=data)
    assert len(clean_data) == 100
    status_code = producer.write_data(data=clean_data)
    assert status_code == 0
