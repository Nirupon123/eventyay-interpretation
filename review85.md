**Production Readiness Review: Changes Requested ❌**

This PR successfully fixes the legacy API key disconnection issues and gracefully handles the `EncryptedTextField` crash, which is great. 

However, it introduces two critical flaws in the OAuth 2.0 flow that block production readiness:

1. **Hardcoded Event Slug:** In `VoxbentoOAuthConnectView`, the `auth_url` hardcodes `&event=testevent2`. This means all organizers, regardless of what event they are managing, will request authorization for `testevent2`. This must be dynamically populated using `event.slug`.
2. **Missing CSRF Validation (State):** While the `state` parameter is generated and passed to the authorization URL, it is **never validated** in `VoxbentoOAuthCallbackView.get()`. This makes the OAuth flow vulnerable to Cross-Site Request Forgery (CSRF). You must pop `voxbento_oauth_state` from the session and ensure it strictly matches `request.GET.get("state")`.

I have already pushed these exact fixes to the branch `fix-oauth-working` on the main `fossasia/eventyay-interpretation` repository. Please merge that branch into yours or apply the following patch:

```python
# Fix 1: Use dynamic event.slug
- f"&event=testevent2"
+ f"&event={event.slug}"

# Fix 2: Validate state in VoxbentoOAuthCallbackView
+ expected_state = request.session.pop("voxbento_oauth_state", None)
+ state = request.GET.get("state")
+ if not expected_state or state != expected_state:
+     messages.error(request, _("OAuth authorization failed: State mismatch (CSRF protection)."))
+     kwargs = {"organizer": event.organizer.slug, "event": event.slug}
+     return redirect(reverse("plugins:interpretation:dashboard", kwargs=kwargs))
```
