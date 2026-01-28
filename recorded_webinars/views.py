# recorded_webinars/views.py
from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import RecordedWebinar
from .serializers import (
    RecordedWebinarFrontendSerializer,
    RecordedWebinarDetailPageSerializer,
)
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.db.models import Q
from .models import RecordedWebinar
from webinars.models import Instructor, WebinarCategory
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from recorded_webinars.utils import user_has_purchased_recorded_webinar


from .serializers import RecordedWebinarDetailPageSerializer


class RecordedWebinarFilterAPIView(APIView):
    def get(self, request):

        # ---------- MONTHS ----------
        months_qs = (
            RecordedWebinar.objects
            .filter(is_published=True)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        months = [
            {
                "label": m["month"].strftime("%B %Y"),
                "value": m["month"].strftime("%Y-%m"),
                "count": m["count"]
            }
            for m in months_qs if m["month"]
        ]

        # ---------- INSTRUCTORS ----------
        instructors_qs = (
            Instructor.objects
            .filter(recordedwebinar__is_published=True)
            .annotate(count=Count("recordedwebinar"))
            .values("id", "name", "count")
        )

        instructors = [
            {
                "label": i["name"],
                "value": i["id"],
                "count": i["count"]
            }
            for i in instructors_qs
        ]

        # ---------- CATEGORIES ----------
        categories_qs = (
            WebinarCategory.objects
            .filter(recorded_webinars__is_published=True)
            .annotate(count=Count("recorded_webinars"))
            .values("id", "name", "count")
        )

        categories = [
            {
                "label": c["name"],
                "value": c["id"],
                "count": c["count"]
            }
            for c in categories_qs
        ]

        return Response({
            "months": months,
            "instructors": instructors,
            "categories": categories
        })
    

    
# ---------------- LIST PAGE ----------------
class RecordedWebinarListAPIView(ListAPIView):
    serializer_class = RecordedWebinarFrontendSerializer

    def get_queryset(self):
        qs = RecordedWebinar.objects.filter(
            is_published=True
        ).select_related(
            "instructor",
            "pricing",
            "category"
        )

        # -------- SEARCH (MATCH LIVE WEBINAR LOGIC) --------
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(instructor__name__icontains=search) |
                Q(instructor__designation__icontains=search) |
                Q(instructor__organization__icontains=search) |
                Q(category__name__icontains=search)
            ).distinct()

        # -------- INSTRUCTOR --------
        instructor = self.request.query_params.get("instructor")
        if instructor:
            qs = qs.filter(instructor_id=instructor)

        # -------- CATEGORY --------
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category_id=category)

        return qs

    def get_serializer_context(self):
        return {"request": self.request}



# ---------------- DETAIL PAGE ----------------


class RecordedWebinarDetailAPIView(RetrieveAPIView):
    serializer_class = RecordedWebinarDetailPageSerializer
    lookup_field = "webinar_id"

    def get_queryset(self):
        return RecordedWebinar.objects.select_related(
            "instructor",
            "pricing",
            "details",
        ).filter(
            is_published=True
        )

    def get_serializer_context(self):
        return {"request": self.request}


class WatchRecordedWebinarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, webinar_id):
        webinar = get_object_or_404(
            RecordedWebinar,
            webinar_id=webinar_id,
            is_published=True
        )

        # ✅ Access only if purchased (recorded or combo)
        if user_has_purchased_recorded_webinar(request.user, webinar):
            return Response(
                {
                    "access": True,
                    "webinar_id": webinar.webinar_id,
                },
                status=status.HTTP_200_OK
            )

        # ❌ No access
        return Response(
            {"detail": "You do not have access to this recorded webinar"},
            status=status.HTTP_403_FORBIDDEN
        )

