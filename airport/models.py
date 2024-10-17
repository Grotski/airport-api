from django.db import models


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Airport(models.Model):
    name = models.CharField(max_length=1000)
    closest_big_city = models.CharField(max_length=500)


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE)
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE)
    ditance = models.IntegerField()


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()
    airplane_type = models.ForeignKey(AirplaneType, on_delete=models.CASCADE)


class Flight(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arriwal_time = models.DateTimeField()

    def __str__(self):
        return str(self.route)

    class Meta:
        ordering = ["-departure_time"]


class Order(models.Model):
    created_at = models.DateTimeField(auto_now=True)


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    fligh = models.ForeignKey(Flight, on_Delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
