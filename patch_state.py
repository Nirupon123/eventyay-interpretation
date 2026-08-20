with open("interpretation/views_oauth.py", "r") as f:
    content = f.read()

state_check = """
        code_verifier = request.session.pop("voxbento_oauth_code_verifier", None)
        if not code_verifier:
            messages.error(request, _("OAuth authorization failed: Missing PKCE code verifier in session."))
            kwargs = {"organizer": event.organizer.slug, "event": event.slug}
            return redirect(reverse("plugins:interpretation:dashboard", kwargs=kwargs))
            
        expected_state = request.session.pop("voxbento_oauth_state", None)
        state = request.GET.get("state")
        if not expected_state or state != expected_state:
            messages.error(request, _("OAuth authorization failed: State mismatch (CSRF protection)."))
            kwargs = {"organizer": event.organizer.slug, "event": event.slug}
            return redirect(reverse("plugins:interpretation:dashboard", kwargs=kwargs))
"""

content = content.replace(
    """        code_verifier = request.session.pop("voxbento_oauth_code_verifier", None)
        if not code_verifier:
            messages.error(request, _("OAuth authorization failed: Missing PKCE code verifier in session."))
            kwargs = {"organizer": event.organizer.slug, "event": event.slug}
            return redirect(reverse("plugins:interpretation:dashboard", kwargs=kwargs))""",
    state_check.strip(),
)

with open("interpretation/views_oauth.py", "w") as f:
    f.write(content)
