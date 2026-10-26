"""Authorization tests for interpretation commons views."""

import pytest
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db

User = get_user_model()


def _room_interpretation_url(event, room, suffix):
    org = event.organizer.slug
    slug = event.slug
    return f"/api/v1/organizers/{org}/events/{slug}/rooms/{room.pk}/interpretation/{suffix}/"


@pytest.fixture
def room(event):
    from eventyay.base.models import Room

    return Room.objects.create(event=event, name="Main Stage")


@pytest.fixture
def restricted_client(client, db, organizer):
    from eventyay.base.models import Team

    user = User.objects.create_user(
        email="restricted@example.com",
        password="testpass123",
        fullname="Restricted",
        locale="en",
    )
    team = Team.objects.create(
        organizer=organizer,
        name="View Only",
        all_events=True,
        can_change_event_settings=False,
    )
    team.members.add(user)
    client.force_login(user)
    return client


def test_anonymous_user_redirected_from_dashboard(client, dashboard_url):
    response = client.get(dashboard_url)

    assert response.status_code in {403, 302}
    if response.status_code == 302:
        assert "login" in response.url.lower() or "account" in response.url.lower()


def test_restricted_user_denied_dashboard(restricted_client, dashboard_url):
    response = restricted_client.get(dashboard_url)

    assert response.status_code in {403, 302}


def test_restricted_user_denied_interpretation_streams_api(restricted_client, event, room):
    response = restricted_client.get(_room_interpretation_url(event, room, "streams"))

    assert response.status_code == 403


def test_restricted_user_denied_interpretation_config_api(restricted_client, event, room):
    response = restricted_client.get(_room_interpretation_url(event, room, "config"))

    assert response.status_code == 403


def test_cross_event_room_action_returns_404(organizer_client, event, connected_event, rooms_url):
    from eventyay.base.models import Event, Room

    other = Event.objects.create(
        organizer=event.organizer,
        name="Other Event",
        slug="otherevent",
        date_from=event.date_from,
        date_to=event.date_to,
        currency="USD",
        locale="en",
        is_public=True,
        live=True,
        email="other@example.com",
    )
    other.plugins = "interpretation"
    other.save(update_fields=["plugins"])
    other_room = Room.objects.create(event=other, name="Other Room")

    response = organizer_client.post(
        rooms_url,
        {
            "interpretation_room_id": str(other_room.pk),
            "interpretation_room_action": "save",
            "room-999-interpreter": "susi",
        },
    )

    assert response.status_code == 404


def _make_authz_request(user, event):
    from types import SimpleNamespace

    from django.contrib.sessions.backends.db import SessionStore
    from django.test import RequestFactory

    rf = RequestFactory()
    req = rf.get("/api/v1/dummy/")
    req.user = user
    req.auth = None
    req.session = SessionStore()
    req.resolver_match = SimpleNamespace(kwargs={"organizer": event.organizer.slug, "event": event.slug})
    return req


def test_attendee_video_permission_admission_vs_non_admission(event, user):
    import datetime
    from types import SimpleNamespace

    from django.utils.timezone import now
    from django_scopes import scope, scopes_disabled
    from eventyay.base.models import Order, OrderPosition, Product

    from interpretation.api import AttendeeVideoPermission

    perm = AttendeeVideoPermission()
    view = SimpleNamespace(event=event)
    req = _make_authz_request(user, event)

    event.settings.set("venueless_all_products", True)
    event.settings.set("venueless_show_public_link", False)

    # 1. Non-admission product (e.g. T-Shirt) - buyer must be denied access
    with scopes_disabled():
        tshirt = Product.objects.create(event=event, name="T-Shirt", default_price=20, admission=False)
        order1 = Order.objects.create(
            event=event,
            status=Order.STATUS_PAID,
            email=user.email,
            datetime=now(),
            expires=now() + datetime.timedelta(days=7),
            total=20,
            locale="en",
        )
        OrderPosition.objects.create(
            order=order1,
            product=tshirt,
            price=20,
            attendee_name_cached="Test User",
            secret="tshirtsecret123",
        )

    with scope(organizer=event.organizer):
        assert perm.has_permission(req, view) is False

    # 2. Admission product (e.g. Conference Ticket) - buyer must be granted access
    with scopes_disabled():
        ticket = Product.objects.create(event=event, name="Conference Ticket", default_price=100, admission=True)
        order2 = Order.objects.create(
            event=event,
            status=Order.STATUS_PAID,
            email=user.email,
            datetime=now(),
            expires=now() + datetime.timedelta(days=7),
            total=100,
            locale="en",
        )
        OrderPosition.objects.create(
            order=order2,
            product=ticket,
            price=100,
            attendee_name_cached="Test User",
            secret="ticketsecret123",
        )

    with scope(organizer=event.organizer):
        assert perm.has_permission(req, view) is True


def test_attendee_video_permission_specific_products(event, user):
    import datetime
    from types import SimpleNamespace

    from django.utils.timezone import now
    from django_scopes import scope, scopes_disabled
    from eventyay.base.models import Order, OrderPosition, Product

    from interpretation.api import AttendeeVideoPermission

    perm = AttendeeVideoPermission()
    view = SimpleNamespace(event=event)
    req = _make_authz_request(user, event)

    event.settings.set("venueless_all_products", False)
    event.settings.set("venueless_show_public_link", False)

    with scopes_disabled():
        prod_video = Product.objects.create(event=event, name="Online Pass", default_price=50, admission=False)
        prod_other = Product.objects.create(event=event, name="Workshop Only", default_price=50, admission=False)

    # Set venueless_products to only prod_video
    event.settings.set("venueless_products", [prod_video.pk])

    # Buyer of prod_other only -> Denied
    with scopes_disabled():
        order = Order.objects.create(
            event=event,
            status=Order.STATUS_PAID,
            email=user.email,
            datetime=now(),
            expires=now() + datetime.timedelta(days=7),
            total=50,
            locale="en",
        )
        pos = OrderPosition.objects.create(
            order=order,
            product=prod_other,
            price=50,
            attendee_name_cached="Test User",
            secret="posother123",
        )

    with scope(organizer=event.organizer):
        assert perm.has_permission(req, view) is False

    # Buyer of prod_video -> Allowed
    with scopes_disabled():
        pos.product = prod_video
        pos.save(update_fields=["product"])

    with scope(organizer=event.organizer):
        assert perm.has_permission(req, view) is True


def test_client_listener_token_admission_permission(client, event, user):
    import datetime
    from unittest.mock import patch

    from django.utils.timezone import now
    from django_scopes import scopes_disabled
    from eventyay.base.models import Order, OrderPosition, Product, Room

    from interpretation.models import RoomInterpretation

    room = Room.objects.create(event=event, name="Stream Hall")
    RoomInterpretation.objects.create(
        room=room,
        interpreter=RoomInterpretation.INTERPRETER_VOXBENTO,
        room_enabled=True,
    )
    url = (
        f"/api/v1/organizers/{event.organizer.slug}/events/{event.slug}/rooms/{room.pk}/interpretation/listener-token/"
    )

    event.settings.set("venueless_all_products", True)
    event.settings.set("venueless_show_public_link", False)

    client.force_login(user)

    # 1. Non-admission product (T-shirt)
    with scopes_disabled():
        tshirt = Product.objects.create(event=event, name="T-Shirt", default_price=20, admission=False)
        order = Order.objects.create(
            event=event,
            status=Order.STATUS_PAID,
            email=user.email,
            datetime=now(),
            expires=now() + datetime.timedelta(days=7),
            total=20,
            locale="en",
        )
        pos = OrderPosition.objects.create(
            order=order,
            product=tshirt,
            price=20,
            attendee_name_cached="Test User",
            secret="tshirtsecret123",
        )

    # Must be denied (403)
    response = client.post(url)
    assert response.status_code == 403

    # 2. Add admission product (Conference Ticket)
    with scopes_disabled():
        ticket = Product.objects.create(event=event, name="Conference Ticket", default_price=100, admission=True)
        pos.product = ticket
        pos.save(update_fields=["product"])

    # Now allowed through permission check
    with patch("interpretation.api.RoomInterpretationViewSet._make_voxbento_request") as mock_req:
        mock_resp = type("MockResp", (), {"ok": True, "json": lambda self: {"token": "mock-token"}})()
        mock_req.return_value = (mock_resp, False, None)
        response = client.post(url)
        assert response.status_code == 200
        assert response.json() == {"token": "mock-token"}
