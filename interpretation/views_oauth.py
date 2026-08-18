import requests
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from eventyay.control.permissions import EventPermissionRequiredMixin

from .models import VoxbentoOAuthGrant


class VoxbentoOAuthConnectView(EventPermissionRequiredMixin, View):
    permission = "can_change_event_settings"

    def get(self, request, *args, **kwargs):
        event = self.request.event
        # In a real setup, client_id and redirect_uri come from eventyay settings
        # We assume they are set via environment or plugin settings
        client_id = "YOUR_CLIENT_ID"
        kwargs = {"organizer": event.organizer.slug, "event": event.slug}
        redirect_uri = self.request.build_absolute_uri(
            reverse("plugins:interpretation:oauth_callback", kwargs=kwargs)
        )

        voxbento_base = "http://localhost:8001"
        auth_url = (
            f"{voxbento_base}/oauth/authorize?response_type=code"
            f"&client_id={client_id}&redirect_uri={redirect_uri}"
            f"&scope=events:read rooms:write booths:read booths:write sessions:manage"
        )
        return redirect(auth_url)


class VoxbentoOAuthCallbackView(EventPermissionRequiredMixin, View):
    permission = "can_change_event_settings"

    def get(self, request, *args, **kwargs):
        event = self.request.event
        code = request.GET.get("code")
        if not code:
            messages.error(request, _("OAuth authorization failed: No code provided."))
            kwargs = {"organizer": event.organizer.slug, "event": event.slug}
        return redirect(reverse("plugins:interpretation:dashboard", kwargs=kwargs))

        client_id = "YOUR_CLIENT_ID"
        client_secret = "YOUR_CLIENT_SECRET"
        kwargs = {"organizer": event.organizer.slug, "event": event.slug}
        redirect_uri = self.request.build_absolute_uri(
            reverse("plugins:interpretation:oauth_callback", kwargs=kwargs)
        )
        voxbento_base = "http://localhost:8001"

        try:
            resp = requests.post(
                f"{voxbento_base}/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                timeout=5.0,
            )
            resp.raise_for_status()
            data = resp.json()

            VoxbentoOAuthGrant.objects.update_or_create(
                event=event,
                defaults={
                    "access_token": data.get("access_token", ""),
                    "refresh_token": data.get("refresh_token", ""),
                    "scopes": data.get("scope", ""),
                },
            )
            messages.success(request, _("Successfully connected to VoxBento!"))
        except Exception as e:
            messages.error(request, _("Failed to exchange OAuth token: ") + str(e))

        kwargs = {"organizer": event.organizer.slug, "event": event.slug}
        return redirect(reverse("plugins:interpretation:dashboard", kwargs=kwargs))
