import os, uuid

from django.core.exceptions import ValidationError
from django.db import models
from airport_service import settings
from django.utils.text import slugify


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Airport(models.Model):
    name = models.CharField(max_length=2000)
    closest_big_city = models.CharField(max_length=1000)
    country = models.CharField(max_length=400)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="routes")
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="route"
    )
    ditance = models.IntegerField()

    class Meta:
        ordering = ["-ditance"]

    def __str__(self):
        return (
            f"{self.source.name} to {self.destination.name} at distance: {self.ditance}"
        )


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def airplane_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"
    return os.path.join("uploads/airplanes/", filename)


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplanes"
    )
    image = models.ImageField(null=True, upload_to=airplane_image_file_path)

    def capacity(self):
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="flights")
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arriwal_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, blank=True, related_name="flights")

    def __str__(self):
        return f"{self.route.source.name} to {self.route.destination.name} at {self.departure_time}"

    class Meta:
        ordering = ["-departure_time"]


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders"
    )
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.created_at)

    class Meta:
        ordering = ["-created_at"]


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    fligh = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        for ticket_attr_value, ticket_attr_name, airplane_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row"),
        ]:
            if ticket_attr_value > getattr(airplane, airplane_attr_name):
                raise error_to_raise(
                    f"{ticket_attr_name} must be less than {airplane_attr_name} in airplane {airplane}"
                )

    def clean(self):
        Ticket.validate_ticket(
            self.row, self.seat, self.fligh.airplane, ValidationError
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert,
            force_update,
            using,
            update_fields,
        )

    def __str__(self):
        return f"row: {self.row}, seat: {self.seat}"

    class Meta:
        unique_together = ["fligh", "row", "seat"]
        ordering = ["row", "seat"]
