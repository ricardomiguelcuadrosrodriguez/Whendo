"""Tests for the trigger parser."""
import pytest

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from server.scheduler.trigger_parser import parse_trigger, _parse_time


class TestParseTime:
    """Tests for the internal _parse_time helper."""

    @pytest.mark.parametrize("inp,expected", [
        ("7am",     (7, 0)),
        ("7:30am",  (7, 30)),
        ("12pm",    (12, 0)),
        ("12am",    (0, 0)),
        ("11pm",    (23, 0)),
        ("23:00",   (23, 0)),
        ("9",       (9, 0)),
        ("6pm",     (18, 0)),
    ])
    def test_valid_times(self, inp, expected):
        assert _parse_time(inp) == expected

    @pytest.mark.parametrize("inp", ["25am", "garbage", "12:99am", ""])
    def test_invalid_times(self, inp):
        with pytest.raises(ValueError):
            _parse_time(inp)


class TestParseTrigger:
    """Tests for the public parse_trigger function."""

    def test_day_at_hour(self):
        t = parse_trigger("day at 7am")
        assert isinstance(t, CronTrigger)

    def test_day_at_hour_minute(self):
        t = parse_trigger("day at 7:30am")
        assert isinstance(t, CronTrigger)

    def test_weekday(self):
        t = parse_trigger("monday at 9am")
        assert isinstance(t, CronTrigger)

    def test_every_prefix(self):
        t = parse_trigger("every monday at 6pm")
        assert isinstance(t, CronTrigger)

    @pytest.mark.parametrize("expr", ["5 minutes", "1 hour", "2 days", "12 hours"])
    def test_intervals(self, expr):
        t = parse_trigger(expr)
        assert isinstance(t, IntervalTrigger)

    def test_raw_cron(self):
        t = parse_trigger("0 7 * * *")
        assert isinstance(t, CronTrigger)

    @pytest.mark.parametrize("expr", ["", "nonsense", "every blah"])
    def test_invalid(self, expr):
        with pytest.raises(ValueError):
            parse_trigger(expr)
