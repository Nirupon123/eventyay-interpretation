from django.db import migrations, models


def _column_names(schema_editor, table):
    with schema_editor.connection.cursor() as cursor:
        return {
            col.name
            for col in schema_editor.connection.introspection.get_table_description(
                cursor, table
            )
        }


def apply_database_changes(apps, schema_editor):
    """Apply schema changes, skipping columns already present from branch-hopping."""
    model = apps.get_model("interpretation", "RoomInterpretation")
    table = model._meta.db_table
    columns = _column_names(schema_editor, table)

    if "susi_session_id" in columns and "backend_session_id" not in columns:
        schema_editor.execute(
            schema_editor.sql_rename_column
            % {
                "table": schema_editor.quote_name(table),
                "old_column": schema_editor.quote_name("susi_session_id"),
                "new_column": schema_editor.quote_name("backend_session_id"),
            }
        )
        columns.remove("susi_session_id")
        columns.add("backend_session_id")

    if "interpreter" not in columns:
        field = models.CharField(
            choices=[("none", "None"), ("susi", "SUSI Translator")],
            default="none",
            max_length=32,
            verbose_name="Interpreter",
        )
        field.set_attributes_from_name("interpreter")
        schema_editor.add_field(model, field)

    if "room_enabled" not in columns:
        field = models.BooleanField(
            default=False,
            help_text=(
                "When enabled, this room can run interpretation using the "
                "selected interpreter."
            ),
            verbose_name="Interpretation enabled for room",
        )
        field.set_attributes_from_name("room_enabled")
        schema_editor.add_field(model, field)

    if "backend_config" not in columns:
        field = models.JSONField(
            blank=True, default=dict, verbose_name="Backend config"
        )
        field.set_attributes_from_name("backend_config")
        schema_editor.add_field(model, field)


def backfill_interpreter_from_session(apps, schema_editor):
    RoomInterpretation = apps.get_model("interpretation", "RoomInterpretation")
    table = RoomInterpretation._meta.db_table
    columns = _column_names(schema_editor, table)
    if "interpreter" not in columns:
        return

    session_column = (
        "backend_session_id"
        if "backend_session_id" in columns
        else "susi_session_id"
    )
    for row in RoomInterpretation.objects.exclude(**{f"{session_column}": ""}):
        if row.interpreter == "none":
            row.interpreter = "susi"
            row.save(update_fields=["interpreter"])


class Migration(migrations.Migration):

    dependencies = [
        ("interpretation", "0003_rename_hls_url_stream_url"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(
                    apply_database_changes,
                    migrations.RunPython.noop,
                ),
            ],
            state_operations=[
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
                    field=models.JSONField(
                        blank=True, default=dict, verbose_name="Backend config"
                    ),
                ),
                migrations.AlterField(
                    model_name="roominterpretation",
                    name="backend_session_id",
                    field=models.CharField(
                        blank=True,
                        help_text=(
                            "Session/tenant ID returned by the active interpreter backend."
                        ),
                        max_length=64,
                        verbose_name="Backend session ID",
                    ),
                ),
            ],
        ),
        migrations.RunPython(
            backfill_interpreter_from_session,
            migrations.RunPython.noop,
        ),
    ]
