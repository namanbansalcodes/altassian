from django.urls import path

from analytics.views import (
    ActivityTimelineView,
    ContentActivityView,
    OverviewView,
    TrackPageViewView,
    UserActivityView,
)

urlpatterns = [
    path('overview/', OverviewView.as_view(), name='analytics-overview'),
    path('user-activity/', UserActivityView.as_view(), name='analytics-user-activity'),
    path('content-activity/', ContentActivityView.as_view(), name='analytics-content-activity'),
    path('activity-timeline/', ActivityTimelineView.as_view(), name='analytics-activity-timeline'),
    path('track-view/', TrackPageViewView.as_view(), name='analytics-track-view'),
]
