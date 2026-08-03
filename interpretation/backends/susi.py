from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from ..models import RoomInterpretation
from ..services import start_stream_session
from ..settings import get_susi_client, is_susi_connected
from ..susi import SusiError


class SusiBackend:
    id = RoomInterpretation.INTERPRETER_SUSI
    label = _("SUSI Translator")

    def is_configured(self, event) -> bool:
        return is_susi_connected(event)

    def start(self, event, interpretation, *, stream_url: str) -> str:
        client = get_susi_client(event)
        return start_stream_session(
            client,
            stream_url,
            transcription_provider=interpretation.transcription_provider,
            translation_provider=interpretation.translation_provider,
        )

    def stop(self, event, interpretation) -> None:
        session_id = interpretation.backend_session_id
        if not session_id:
            return
        client = get_susi_client(event)
        try:
            client.stop_session(session_id)
        except SusiError:
            raise
