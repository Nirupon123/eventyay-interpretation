from django.db import migrations, models


def backfill_interpreter_from_session(apps, schema_editor):
    RoomInterpretation = apps.get_model("interpretation", "RoomInterpretation")
    for row in RoomInterpretation.objects.exclude(backend_session_id=""):
        row.interpreter = "susi"
        row.save(update_fields=["interpreter"])


class Migration(migrations.Migration):

    dependencies = [
        ("interpretation", "0003_rename_hls_url_stream_url"),
    ]

    operations = [
        migrations.RenameField(
            model_name="roominterpretation",
            old_name="susi_session_id",
            new_name="backend_session_id",
        ),
        migrations.AddField(
            model_name="roominterpretation",
            name="interpreter",
            field=models.CharField(
                choices=[("none", "None"), ("susi", "SUSI Translator")],
                default="none",
                max_length=32,
                verbose_name="Interpreter",
            ),
        ),
        migrations.AddField(
            model_name="roominterpretation",
            name="room_enabled",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "When enabled, this room can run interpretation using the "
                    "selected interpreter."
                ),
                verbose_name="Interpretation enabled for room",
            ),
        ),
        migrations.AddField(
            model_name="roominterpretation",
            name="backend_config",
            field=models.JSONField(blank=True, default=dict, verbose_name="Backend config"),
        ),
        migrations.RunPython(
            backfill_interpreter_from_session,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="roominterpretation",
            name="backend_session_id",
            field=models.CharField(
                blank=True,
                help_text="Session/tenant ID returned by the active interpreter backend.",
                max_length=64,
                verbose_name="Backend session ID",
            ),
        ),
    ]
