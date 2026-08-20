# Change Impact Map

- **Adding a new webhook event**: Modify `interpretation/views_webhooks.py` and potentially add a handler in `tasks.py`.
- **Changing OAuth scopes**: Update `interpretation/views_oauth.py` and ensure the request to VoxBento reflects the new scope.
- **Adding a new organizer setting**: Update `interpretation/forms.py`, `interpretation/models.py`, and `templates/interpretation/`.
- **Modifying the video room UI**: This requires Phase 4 integration in the `eventyay-host` core (Vue.js frontend), not just this Django plugin!
