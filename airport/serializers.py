from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Flight, Airplane, AirplaneType, Route, Ticket, Order, Crew, Airport
from django.db import transaction


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = (
            "id",
            "name",
            "closest_big_city",
            "country",
        )


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "ditance",
        )


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")
    destination = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
        )


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(many=True, read_only=True)
    destination = AirportSerializer(many=True, read_only=True)

    class Meta:
        model = Route
        fields = (
            "id",
            "source",
            "destination",
            "ditance",
        )


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = (
            "id",
            "name",
        )


class AirplaneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
        )


class AirplaneListSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugRelatedField(read_only=True, slug_field="name")

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "capacity",
            "airplane_type",
            "image",
        )


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = AirplaneTypeSerializer(many=True, read_only=True)

    class Meta:
        model = Airplane
        fields = (
            "id",
            "name",
            "rows",
            "seats_in_row",
            "capacity",
            "airplane_type",
            "image",
        )


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "image")


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arriwal_time",
        )


class FlightListSerializer(FlightSerializer):
    route = RouteListSerializer(many=True, read_only=True)
    airplane_name = serializers.CharField(read_only=True, source="airplane.name")
    airplane_image = serializers.ImageField(read_only=True, source="airplane.image")
    airplane_capacity = serializers.IntegerField(
        source="airplane.capacity", read_only=True
    )
    airplane_type = serializers.CharField(
        source="airplane.airplane_type.name", read_only=True
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane_name",
            "airplane_image",
            "airplane_capacity",
            "airplane_type",
            "departure_time",
            "arriwal_time",
        )


class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(many=True, read_only=True)
    airplane = AirplaneSerializer(many=True, read_only=True)
    departure_time = serializers.DateTimeField(read_only=True)
    arriwal_time = serializers.DateTimeField(read_only=True)
    tickets_avilable = serializers.IntegerField(read_only=True)
    crew = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arriwal_time",
            "tickets_avilable",
            "crew",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, data):
        data = super(TicketSerializer, self).validate(data)
        Ticket.validate_ticket(
            data["row"], data["seat"], data["fligh"].airplane, ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "fligh")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = (
            "id",
            "tickets",
            "created_at",
        )

    @transaction.atomic
    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        order = Order.objects.create(**validated_data)
        for ticket_data in tickets_data:
            Ticket.objects.create(**ticket_data, order=order)
        return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
