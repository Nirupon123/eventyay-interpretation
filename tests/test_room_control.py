import pytest

from interpretation.utils import (
    MAX_BACKEND_CONFIG_BYTES,
    MAX_TARGET_LANGUAGES,
    normalize_target_languages,
    validate_backend_config,
    validate_target_language_codes,
)


def test_normalize_target_languages_from_comma_string():
    assert normalize_target_languages("de, fr, de, es") == ["de", "fr", "es"]


def test_normalize_target_languages_from_list():
    assert normalize_target_languages(["de", "fr"]) == ["de", "fr"]


def test_normalize_target_languages_empty():
    assert normalize_target_languages("") == []
    assert normalize_target_languages([]) == []


def test_validate_backend_config_rejects_non_object():
    with pytest.raises(ValueError, match="object"):
        validate_backend_config(["bad"])


def test_validate_backend_config_rejects_oversized_payload():
    huge = {"k": "x" * (MAX_BACKEND_CONFIG_BYTES + 1)}
    with pytest.raises(ValueError, match="too large"):
        validate_backend_config(huge)


def test_validate_target_language_codes_rejects_too_many():
    codes = [f"l{i}" for i in range(MAX_TARGET_LANGUAGES + 1)]
    with pytest.raises(ValueError, match="Too many"):
        validate_target_language_codes(codes)


def test_disconnect_susi_stops_event_sessions(monkeypatch):
    from interpretation.settings import disconnect_susi

    stopped = []

    def fake_stop_all(event):
        stopped.append(event)

    monkeypatch.setattr(
        "interpretation.room_control.stop_all_event_sessions",
        fake_stop_all,
    )

    class _FakeSettings:
        def __init__(self):
            self.data = {}

        def set(self, key, value):
            self.data[key] = value

    event = type("E", (), {"settings": _FakeSettings()})()
    disconnect_susi(event)
    assert stopped == [event]
    assert event.settings.data["interpretation_auth_token"] == ""
