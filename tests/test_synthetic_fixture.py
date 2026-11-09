"""Contract-only tests for deliberately fictional public CI data."""
import json
import unittest
from datetime import datetime
from pathlib import Path

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/fictional_disclosure.json"


def parse_clock(value):
    result = datetime.fromisoformat(value)
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Clock must include timezone")
    return result


class FictionalDisclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.records = cls.payload["records"]

    def test_explicit_fictional_source(self):
        self.assertIs(self.payload["synthetic_only"], True)
        self.assertEqual(self.payload["source"], "FICTIONAL-NOT-SEC")

    def test_unique_event_ids(self):
        ids = [item["event_id"] for item in self.records]
        self.assertTrue(ids)
        self.assertEqual(len(ids), len(set(ids)))

    def test_observation_clock_is_not_transaction_clock(self):
        for item in self.records:
            event = parse_clock(item["transaction_at"])
            filed = parse_clock(item["filed_at"])
            seen = parse_clock(item["first_seen_at"])
            self.assertLessEqual(event, filed)
            self.assertLessEqual(filed, seen)

    def test_reject_naive_timestamp(self):
        with self.assertRaisesRegex(ValueError, "timezone"):
            parse_clock("2026-01-10T09:00:00")


if __name__ == "__main__":
    unittest.main()
