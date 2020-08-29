from django.db import models
import datetime

class Room(models.Model):
    """
        Adding new room with specific name, capacity and information if there is projector available in room.
    """
    name = models.CharField(max_length=15)
    capacity = models.PositiveIntegerField()
    projector_availability = models.BooleanField(default=False)

    def get_status(self):
        today = datetime.datetime.today().date()
        try:
            RoomReservation.objects.get(date=today, room_id=self)
            return "reserved"
        except:
            return "available"

class RoomReservation(models.Model):
    """
        Reserving room for specific date.
    """
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
    date = models.DateField()
    comment = models.TextField(null=True)

    class Meta:
        unique_together = ('room_id', 'date')

