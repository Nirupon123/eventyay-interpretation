import django.db.models.deletion
from django.db import migrations, models

from interpretation.fields import EncryptedTextField, get_fernet


def encrypt_existing_tokens(apps, schema_editor):
    VoxbentoOAuthGrant = apps.get_model("interpretation", "VoxbentoOAuthGrant")
    fernet = get_fernet()
    
    if not fernet:
        if VoxbentoOAuthGrant.objects.exists():
            raise ValueError(
                "EVENTYAY_VOXBENTO_FERNET_KEYS is required to encrypt existing plaintext tokens. "
                "Please provision this environment variable before running the migration."
            )
        return

    for grant in VoxbentoOAuthGrant.objects.all():
        updated = False
        
        # We rely on the fallback in EncryptedTextField.from_db_value to return plaintext
        # if decryption fails (which it will for existing plaintext rows).
        if grant.access_token and not grant.access_token.startswith("gAAAAA"):
            updated = True
            
        if grant.refresh_token and not grant.refresh_token.startswith("gAAAAA"):
            updated = True

        if updated:
            # Re-saving the grant will trigger EncryptedTextField.get_prep_value,
            # which will encrypt the plaintext value using Fernet.
            grant.save(update_fields=["access_token", "refresh_token"])


def reverse_encrypt(apps, schema_editor):
    # We do not automatically decrypt on rollback to prevent accidental plaintext leakage.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("interpretation", "0010_voxbentooauthgrant"),
    ]

    operations = [
        migrations.AddField(
            model_name="voxbentooauthgrant",
            name="needs_reauth",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="voxbentooauthgrant",
            name="webhook_secret_key",
            field=EncryptedTextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="voxbentooauthgrant",
            name="webhook_subscription_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="voxbentooauthgrant",
            name="access_token",
            field=EncryptedTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="voxbentooauthgrant",
            name="refresh_token",
            field=EncryptedTextField(blank=True, null=True),
        ),
        migrations.RunPython(encrypt_existing_tokens, reverse_encrypt),
    ]
