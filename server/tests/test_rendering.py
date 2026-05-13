"""Tests for Jinja2 rendering of action config values."""
import pytest

from server.actions.rendering import render_value


def test_string_without_placeholders_is_unchanged():
    assert render_value("hello world", {}) == "hello world"


def test_string_with_placeholder_renders_against_context():
    assert (
        render_value("Hi {{ name }}!", {"name": "Jefe"}) == "Hi Jefe!"
    )


def test_dict_is_walked_recursively():
    result = render_value(
        {"message": "Hoy llueve en {{ city }}", "level": 1},
        {"city": "Lima"},
    )
    assert result == {"message": "Hoy llueve en Lima", "level": 1}


def test_list_is_walked_recursively():
    result = render_value(
        ["plain", "{{ x }}", 42],
        {"x": "templated"},
    )
    assert result == ["plain", "templated", 42]


def test_non_string_values_pass_through():
    assert render_value(42, {}) == 42
    assert render_value(True, {}) is True
    assert render_value(None, {}) is None


def test_undefined_variable_raises():
    from jinja2.exceptions import UndefinedError

    with pytest.raises(UndefinedError):
        render_value("{{ missing }}", {})
