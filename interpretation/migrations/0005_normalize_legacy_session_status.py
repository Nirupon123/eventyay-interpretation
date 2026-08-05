from django.db import migrations


def normalize_legacy_status(apps, schema_editor):
    RoomInterpretation = apps.get_model("interpretation", "RoomInterpretation")
    RoomInterpretation.objects.filter(status__in=["stopped", "error"]).update(
        status="idle",
        backend_session_id="",
    )


class Migration(migrations.Migration):

    dependencies = [
        ("interpretation", "0004_per_room_interpreter"),
    ]

    operations = [
        migrations.RunPython(normalize_legacy_status, migrations.RunPython.noop),
    ]
