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
            "instructor",
            "pricing"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context




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
