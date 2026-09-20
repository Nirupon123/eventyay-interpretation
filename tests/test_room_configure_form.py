"""Tests for RoomConfigureForm."""

import pytest

from interpretation.forms import RoomConfigureForm
from interpretation.models import RoomInterpretation


class _FakeEvent:
    id = 1
    pk = 1

    def __int__(self):
        return self.id

    def get_plugins(self):
        return ["interpretation"]

    class settings:
        @staticmethod
        def get(key, default=None, as_type=str):
            return default


pytestmark = pytest.mark.django_db


def test_room_configure_form_lists_interpreters():
    form = RoomConfigureForm(event=_FakeEvent())
    ids = [choice[0] for choice in form.fields["interpreter"].choices]
    assert RoomInterpretation.INTERPRETER_NONE in ids
    assert RoomInterpretation.INTERPRETER_SUSI not in ids


def test_room_configure_form_accepts_interpreter_and_enabled(event):
    from interpretation.models import VoxbentoOAuthGrant

    event.plugins = "interpretation"
    event.save(update_fields=["plugins"])
    event.settings.set("interpretation_voxbento_base_url", "https://v.example")
    VoxbentoOAuthGrant.objects.create(event=event, access_token="t", is_disconnected=False)

    form = RoomConfigureForm(
        event=event,
        data={
            "interpreter": RoomInterpretation.INTERPRETER_VOXBENTO,
            "room_enabled": True,
        },
    )
    assert form.is_valid(), form.errors
    assert form.cleaned_data["interpreter"] == RoomInterpretation.INTERPRETER_VOXBENTO
    assert form.cleaned_data["room_enabled"] is True


def test_room_configure_form_validates_transcription_fields(event):
    form = RoomConfigureForm(
        event=event,
        data={
            "interpreter": RoomInterpretation.INTERPRETER_VOXBENTO,
            "room_enabled": True,
            "enable_transcription": True,
            "transcription_provider": "",
            "transcription_model": "",
        },
    )
    assert not form.is_valid()
    assert "transcription_provider" in form.errors
    assert "transcription_model" in form.errors

    form = RoomConfigureForm(
        event=event,
        data={
            "interpreter": RoomInterpretation.INTERPRETER_VOXBENTO,
            "room_enabled": True,
            "enable_transcription": True,
            "transcription_provider": "local",
            "transcription_model": "base",
        },
    )
    assert form.is_valid()


def test_room_configure_form_validates_translation_fields(event):
    form = RoomConfigureForm(
        event=event,
        data={
            "interpreter": RoomInterpretation.INTERPRETER_VOXBENTO,
            "room_enabled": True,
            "enable_transcription": False,
            "enable_translation": True,
            "translation_provider": "local",
            "translation_model": "nllb-200-distilled-600M",
        },
    )
    assert not form.is_valid()
    assert "enable_translation" in form.errors  # Requires transcription

    form = RoomConfigureForm(
        event=event,
        data={
            "interpreter": RoomInterpretation.INTERPRETER_VOXBENTO,
            "room_enabled": True,
            "enable_transcription": True,
            "transcription_provider": "local",
            "transcription_model": "base",
            "enable_translation": True,
            "translation_provider": "",
            "translation_model": "",
        },
    )
    assert not form.is_valid()
    assert "translation_provider" in form.errors
    assert "translation_model" in form.errors

    form = RoomConfigureForm(
        event=event,
        data={
            "interpreter": RoomInterpretation.INTERPRETER_VOXBENTO,
            "room_enabled": True,
            "enable_transcription": True,
            "transcription_provider": "local",
            "transcription_model": "base",
            "enable_translation": True,
            "translation_provider": "local",
            "translation_model": "nllb-200-distilled-600M",
        },
    )
    assert form.is_valid()
