from rest_framework.generics import ListAPIView, RetrieveAPIView
from .models import LiveWebinar
from .serializers import (
    LiveWebinarSerializer,
    LiveWebinarDetailSerializer,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncMonth

from .models import LiveWebinar, Instructor
from .pagination import LiveWebinarPagination



from django.db.models import Q

class LiveWebinarListAPIView(ListAPIView):
    serializer_class = LiveWebinarSerializer
    pagination_class = LiveWebinarPagination

    def get_queryset(self):
        queryset = LiveWebinar.objects.select_related(
            "instructor",
            "pricing",
            "category"
        )

        # -------- SEARCH --------
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(instructor__name__icontains=search) |
                Q(instructor__designation__icontains=search) |
                Q(instructor__organization__icontains=search) |
                Q(category__name__icontains=search)
            ).distinct()


        # -------- MONTH FILTER (YYYY-MM) --------
        month = self.request.query_params.get("month")
        if month:
            try:
                year, month_num = month.split("-")
                queryset = queryset.filter(
                    start_datetime__year=year,
                    start_datetime__month=month_num
                )
            except ValueError:
                pass  # ignore invalid format

        # -------- INSTRUCTOR FILTER --------
        instructor = self.request.query_params.get("instructor")
        if instructor:
            queryset = queryset.filter(instructor_id=instructor)

        # -------- CATEGORY FILTER --------
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


# webinars/views.py



class LiveWebinarFilterAPIView(APIView):
    def get(self, request):

        # -------- MONTHS --------
        months_qs = (
            LiveWebinar.objects
            .annotate(month=TruncMonth("start_datetime"))
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

        # -------- INSTRUCTORS --------
        instructors_qs = (
            Instructor.objects
            .filter(livewebinar__isnull=False)
            .annotate(count=Count("livewebinar"))
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

        # -------- CATEGORIES (if exists) --------
        categories = []
        if hasattr(LiveWebinar, "category"):
            categories_qs = (
                LiveWebinar.objects
                .values("category__id", "category__name")
                .annotate(count=Count("id"))
            )

            categories = [
                {
                    "label": c["category__name"],
                    "value": c["category__id"],
                    "count": c["count"]
                }
                for c in categories_qs if c["category__name"]
            ]

        return Response({
            "months": months,
            "instructors": instructors,
            "categories": categories
        })


class LiveWebinarDetailAPIView(RetrieveAPIView):
    queryset = LiveWebinar.objects.select_related(
        "instructor",
        "pricing",
        "webinaroverview",
        "webinarwhyattend",
        "webinarbenefit",
        "webinarareacovered",
    )
    serializer_class = LiveWebinarDetailSerializer
    lookup_field = "webinar_id"
