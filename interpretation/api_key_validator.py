import logging

import requests

logger = logging.getLogger(__name__)


def validate_provider_key(provider: str, api_key: str) -> bool:
    """
    Validates a third-party AI provider API key by making a lightweight
    authenticated request to their models or auth endpoint.
    Returns True if valid (or if we can't definitively prove it's invalid due to network).
    Returns False if the provider explicitly rejects the key (401/403).
    """
    if not api_key:
        return False

    try:
        if provider in ["openai", "translation_openai"]:
            resp = requests.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5.0,
            )
            if resp.status_code in (401, 403):
                return False
            return True

        elif provider == "deepgram":
            resp = requests.get(
                "https://api.deepgram.com/v1/projects",
                headers={"Authorization": f"Token {api_key}"},
                timeout=5.0,
            )
            if resp.status_code in (401, 403):
                return False
            return True

        elif provider == "nvidia":
            resp = requests.get(
                "https://integrate.api.nvidia.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5.0,
            )
            if resp.status_code in (401, 403):
                return False
            return True

        elif provider == "elevenlabs":
            resp = requests.get(
                "https://api.elevenlabs.io/v1/models",
                headers={"xi-api-key": api_key},
                timeout=5.0,
            )
            if resp.status_code in (401, 403):
                return False
            return True

        elif provider == "openrouter":
            resp = requests.get(
                "https://openrouter.ai/api/v1/auth/key",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5.0,
            )
            if resp.status_code in (401, 403):
                return False
            return True

        elif provider == "gemini":
            resp = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}",
                timeout=5.0,
            )
            if resp.status_code in (400, 401, 403):
                return False
            return True

        elif provider == "anthropic":
            resp = requests.get(
                "https://api.anthropic.com/v1/models",
                headers={"x-api-key": api_key, "anthropic-version": "2023-06-01"},
                timeout=5.0,
            )
            if resp.status_code in (401, 403):
                return False
            return True

        elif provider == "groq":
            resp = requests.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=5.0,
            )
            if resp.status_code in (401, 403):
                return False
            return True

    except requests.RequestException as e:
        logger.warning(f"Failed to reach {provider} API for key validation: {e}")
        # Default to True on network error to avoid blocking the user from saving
        return True

    return True
