from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlightViewSet, AirplaneViewSet, AirplaneTypeViewSet, RouteViewSet, OrderViewSet, \
    CrewViewSet, AirportViewSet

router = DefaultRouter()
router.register("flights", FlightViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("routes", RouteViewSet)
router.register("orders", OrderViewSet)
router.register("crews", CrewViewSet)
router.register("airports", AirportViewSet)

urlpatterns = [
    path("", include(router.urls)),
]


app_name = "airport"
