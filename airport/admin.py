from django.contrib import admin

from .models import Airport, Airplane, AirplaneType, Crew, Flight, Route


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ("name", "closest_big_city")
    search_fields = ("closest_big_city",)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "ditance")
    search_fields = ("source__name", "destination__name")


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ("route", "airplane", "departure_time", "arriwal_time")
    search_fields = ("route__source__name", "route__destination__name")
    list_filter = ("airplane__airplane_type", "airplane__rows")


admin.site.register(Airplane)
admin.site.register(AirplaneType)
admin.site.register(Crew)
