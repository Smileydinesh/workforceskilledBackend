# recorded_webinars/views.py
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import RecordedWebinar, RecordedWebinarDetail
from .serializers import (
    RecordedWebinarFrontendSerializer,
    RecordedWebinarDetailPageSerializer,
)
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404
from .models import RecordedWebinarDetail
from .serializers import RecordedWebinarDetailPageSerializer


# ---------------- LIST PAGE ----------------
class RecordedWebinarListAPIView(ListAPIView):
    serializer_class = RecordedWebinarFrontendSerializer

    def get_queryset(self):
        return RecordedWebinar.objects.filter(is_published=True).select_related(
            "instructor",
            "pricing",
        )

    def get_serializer_context(self):
        return {"request": self.request}


# ---------------- DETAIL PAGE ----------------



class RecordedWebinarDetailPageAPIView(RetrieveAPIView):
    serializer_class = RecordedWebinarDetailPageSerializer

    def get_object(self):
        webinar_id = self.kwargs["webinar_id"]
        return get_object_or_404(
            RecordedWebinarDetail.objects.select_related(
                "webinar",
                "webinar__pricing",
                "webinar__instructor",
            ),
            webinar__webinar_id=webinar_id,
            webinar__is_published=True,
        )

    def get_serializer_context(self):
        return {"request": self.request}


