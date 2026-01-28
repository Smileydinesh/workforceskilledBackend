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

from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone

from subscriptions.utils import user_has_active_live_subscription
from webinars.utils import user_has_purchased_live_webinar

from datetime import timedelta
from django.db.models import F, ExpressionWrapper, DateTimeField

from django.db.models import Q

from recorded_webinars.models import RecordedWebinar  # adjust app name

from webinars.serializers import LiveWebinarSerializer
from recorded_webinars.serializers import RecordedWebinarFrontendSerializer



class LiveWebinarListAPIView(ListAPIView):
    serializer_class = LiveWebinarSerializer
    pagination_class = LiveWebinarPagination

    def get_queryset(self):
        now = timezone.now()

        # 🔥 Show webinars from last 48 hours + future
        cutoff_time = now - timedelta(hours=48)

        queryset = (
            LiveWebinar.objects
            .select_related("instructor", "pricing", "category")
            .filter(start_datetime__gte=cutoff_time)
            .order_by("start_datetime")
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

        # -------- MONTH FILTER --------
        month = self.request.query_params.get("month")
        if month:
            try:
                year, month_num = month.split("-")
                queryset = queryset.filter(
                    start_datetime__year=year,
                    start_datetime__month=month_num
                )
            except ValueError:
                pass

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


class JoinLiveWebinarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, webinar_id):
        webinar = get_object_or_404(
            LiveWebinar,
            webinar_id=webinar_id
        )

        # ❌ Webinar not started
        if webinar.start_datetime > timezone.now():
            return Response(
                {"detail": "Webinar has not started yet"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ❌ Webinar ended
        if timezone.now() > webinar.end_datetime:
            return Response(
                {"detail": "Webinar has already ended"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ ACCESS via subscription
        if user_has_active_live_subscription(request.user):
            return Response({
                "access": True,
                "access_type": "SUBSCRIPTION",
                "webinar_id": webinar.webinar_id,
            })

        # ✅ ACCESS via purchase
        if user_has_purchased_live_webinar(request.user, webinar):
            return Response({
                "access": True,
                "access_type": "PURCHASE",
                "webinar_id": webinar.webinar_id,
            })

        # ❌ NO ACCESS
        return Response(
            {"detail": "You do not have access to this live webinar"},
            status=status.HTTP_403_FORBIDDEN
        )


class GlobalSearchAPIView(APIView):
    def get(self, request):
        query = request.GET.get("q", "").strip()

        if not query:
            return Response({
                "live_webinars": [],
                "recorded_webinars": []
            })

        # -------- LIVE WEBINARS --------
        live_qs = LiveWebinar.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(instructor__name__icontains=query) |
            Q(instructor__designation__icontains=query) |
            Q(category__name__icontains=query),
            is_test=False
        ).select_related(
            "instructor", "category", "pricing"
        ).distinct()

        # -------- RECORDED WEBINARS --------
        recorded_qs = RecordedWebinar.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(instructor__name__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related(
            "instructor", "category", "pricing"
        ).distinct()

        return Response({
            "live_webinars": LiveWebinarSerializer(
                live_qs, many=True, context={"request": request}
            ).data,
            "recorded_webinars": RecordedWebinarFrontendSerializer(
                recorded_qs, many=True, context={"request": request}
            ).data,
        })

from rest_framework.views import APIView
from rest_framework.response import Response
from webinars.models import Instructor

class InstructorListAPIView(APIView):
    def get(self, request):
        instructors = Instructor.objects.all().order_by("name")

        data = [
            {
                "id": i.id,
                "name": i.name,
                "photo": request.build_absolute_uri(i.photo.url),
                "designation": i.designation,
            }
            for i in instructors
        ]

        return Response(data)
