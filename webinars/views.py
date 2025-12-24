from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import LiveWebinar
from .serializers import (
    LiveWebinarSerializer,
    LiveWebinarDetailSerializer,
)


class LiveWebinarListAPIView(ListAPIView):
    serializer_class = LiveWebinarSerializer

    def get_queryset(self):
        return LiveWebinar.objects.select_related(
            "instructor", "pricing"
        ).filter(status__in=["UPCOMING", "LIVE"])

    def get_serializer_context(self):
        return {"request": self.request}



class LiveWebinarDetailAPIView(RetrieveAPIView):
    queryset = LiveWebinar.objects.select_related(
        "instructor",
        "pricing"
    ).prefetch_related(
        "webinaroverview_set",
        "webinarwhyattend_set",
        "webinarbenefit_set",
        "webinarareacovered_set",
    )
    serializer_class = LiveWebinarDetailSerializer
    lookup_field = "webinar_id"
