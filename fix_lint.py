with open("interpretation/backends/voxbento_credentials.py", "r") as f:
    content = f.read()

content = content.replace(
    '                logger.error("Failed to delete VoxBento webhook subscription %s for event %s: %s", grant.webhook_subscription_id, event.id, str(e))',
    """                logger.error(
                    "Failed to delete VoxBento webhook subscription %s for event %s: %s",
                    grant.webhook_subscription_id,
                    event.id,
                    str(e),
                )""",
)

with open("interpretation/backends/voxbento_credentials.py", "w") as f:
    f.write(content)

with open("interpretation/views.py", "r") as f:
    content = f.read()

content = content.replace(
    '            messages.warning(request, _("VoxBento requires reauthorization. Please reconnect via the Configure interpreters page."))',
    """            messages.warning(
                request,
                _("VoxBento requires reauthorization. Please reconnect via the Configure interpreters page.")
            )""",
)

with open("interpretation/views.py", "w") as f:
    f.write(content)

with open("tests/conftest.py", "r") as f:
    content = f.read()

import re

content = re.sub(
    r"def apply_voxbento_event_credentials\(event\):\n    for key, value in VOXBENTO_EVENT_CREDENTIALS.items\(\):\n        event.settings.set\(key, value\)\n",
    "",
    content,
    count=1,
)

with open("tests/conftest.py", "w") as f:
    f.write(content)
