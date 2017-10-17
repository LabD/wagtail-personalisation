from __future__ import absolute_import, unicode_literals

import datetime

import pytest

from tests.factories.segment import SegmentFactory
from wagtail_personalisation.models import Segment
from wagtail_personalisation.rules import TimeRule, VisitCountRule


@pytest.mark.django_db
def test_session_added_to_static_segment_at_creation(rf, site, client):
    session = client.session
    session.save()
    client.get(site.root_page.url)

    segment = SegmentFactory(type=Segment.TYPE_STATIC)
    VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)

    assert session.session_key in segment.sessions.values_list('session_key', flat=True)


@pytest.mark.django_db
def test_session_not_added_to_static_segment_after_creation(rf, site, client):
    segment = SegmentFactory(type=Segment.TYPE_STATIC)
    VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)

    session = client.session
    session.save()
    client.get(site.root_page.url)

    assert not segment.sessions.all()


@pytest.mark.django_db
def test_session_added_to_static_segment_after_creation(rf, site, client):
    segment = SegmentFactory(type=Segment.TYPE_STATIC, count=1)
    VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)

    session = client.session
    session.save()
    client.get(site.root_page.url)

    assert session.session_key in segment.sessions.values_list('session_key', flat=True)


@pytest.mark.django_db
def test_session_not_added_to_static_segment_after_full(rf, site, client):
    segment = SegmentFactory(type=Segment.TYPE_STATIC, count=1)
    VisitCountRule.objects.create(counted_page=site.root_page, segment=segment)

    session = client.session
    session.save()
    client.get(site.root_page.url)

    second_session = client.session
    second_session.create()
    client.get(site.root_page.url)

    assert session.session_key != second_session.session_key
    assert segment.sessions.count() == 1
    assert session.session_key in segment.sessions.values_list('session_key', flat=True)
    assert second_session.session_key not in segment.sessions.values_list('session_key', flat=True)


@pytest.mark.django_db
def test_sessions_not_added_to_static_segment_if_rule_not_static():
    segment = SegmentFactory(type=Segment.TYPE_STATIC)
    TimeRule.objects.create(
        start_time=datetime.time(8, 0, 0),
        end_time=datetime.time(23, 0, 0),
        segment=segment)

    assert not segment.sessions.all()
