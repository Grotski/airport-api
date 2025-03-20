from django.shortcuts import render
from django.db.models import F, Count
from datetime import datetime
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from .models import (
    Flight,
    Airplane,
    AirplaneType,
    Route,
    Order,
    Crew,
    Airport
)
from .serializers import (
    FlightSerializer,
    FlightListSerializer,
    FlightDetailSerializer,
    AirplaneSerializer,
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    AirplaneImageSerializer,
    AirplaneTypeSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    OrderSerializer,
    CrewSerializer,
    AirportSerializer,
    OrderListSerializer
)

from .permissions import IsAdminOrIfAuthenticatedReadOnly


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)
    
    def create(self, request, *args, **kwargs):
        is_many = isinstance(request.data, list)

        serialize = self.get_serializer(data=request.data, many=is_many)
        serialize.is_valid(raise_exception=True)
        self.perform_create(serialize)
        return Response(serialize.data, status=status.HTTP_201_CREATED)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


    @staticmethod
    def _params_to_ints(qs):
        """Return str IDs to Integer IDs"""
        return [int(id) for id in qs.split(",")]

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        distance = self.request.query_params.get("distance")

        queryset = self.queryset
        if distance:
            queryset = queryset.filter(distance__lte=distance)
        if source and destination:
            source = self._params_to_ints(source)
            destination = self._params_to_ints(destination)
            queryset = queryset.filter(source__id__in=source).filter(
                destination__id__in=destination
            )
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer
        return RouteSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="source",
                type={type: "list", "items": {"type": "number"}},
                description="Filter by source ID",
            ),
            OpenApiParameter(
                name="destination",
                type={type: "list", "items": {"type": "number"}},
                description="Filter by destination ID",
            ),
            OpenApiParameter(
                name="distance",
                type=OpenApiTypes.INT,
                description="Filter by distance",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)



class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer
        if self.action == "retrieve":
            return AirplaneDetailSerializer
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        airplane = self.get_object()
        serializer = self.get_serializer(airplane, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = (
        Flight.objects.all()
        .select_related("route", "airplane")
        .annotate(
            tickets_avilable=(
                F("airplane__rows")
                * F("airplane__seats_in_row")
                - Count("tickets")
            )
        )
    )
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        date = self.request.query_params.get("date")
        route_id_str = self.request.query_params.get("route")
        airplane_id_str = self.request.query_params.get("airplane")

        queryset = self.queryset

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            queryset = queryset.filter(departure_time__date=date)

        if route_id_str:
            queryset = queryset.filter(route_id=int(route_id_str))
        
        if airplane_id_str:
            queryset = queryset.filter(airplane_id=int(airplane_id_str))

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrive":
            return FlightDetailSerializer
        return FlightSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="route",
                type={
                    "type": "list",
                    "items": {
                        "type": "number",
                    },
                },
                description="Filter by route id",
            ),
            OpenApiParameter(
                name="airplane",
                type={
                    "type": "list",
                    "items": {
                        "type": "number"
                    },
                },
                description="Filter by airplane id",
            ),
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.DATE,
                description="Filter by date",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """List of Flights"""
        return super().list(request, *args, **kwargs)


class OrderPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 100


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet):
    queryset = Order.objects.prefetch_related("tickets__fligh__route", "tickets__fligh__airplane")
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
