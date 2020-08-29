from django.shortcuts import render, redirect
from django.views import View
from room_res.models import Room, RoomReservation
import datetime

def index(request):
    return render(request, 'base.html')

class AddRoomView(View):
    def get(self, request):
        return render(request, "add_room.html")

    def post(self, request):
        name = request.POST.get("name")
        capacity = request.POST.get("capacity")
        capacity = int(capacity) if capacity else 0
        projector = request.POST.get("projector") == "on"

        if not name:
            return render(request, "add_room.html", context={"error": "Enter correct Room name"})
        if capacity <= 0:
            return render(request, "add_room.html", context={"error": "Capacity must be more than zero"})
        if Room.objects.filter(name=name).first():
            return render(request, "add_room.html", context={"error": "This Room already exist"})

        Room.objects.create(name=name, capacity=capacity, projector_availability=projector)
        return redirect("/rooms/")


class RoomListView(View):
    def get(self, request):
        rooms = Room.objects.all()
        context = {'rooms':rooms}
        for room in rooms:
            reservation_dates = [reservation.date for reservation in room.roomreservation_set.all()]
            room.reserved = datetime.date.today() in reservation_dates
        return render(request, 'rooms.html', context)


def room_delete(request, id):
    if request.method == "GET":
        return render(request, 'delete_room.html', {'rooms':Room.objects.get(pk=id)})
    else:
        if request.POST['submit'] == 'Yes':
            room = Room.objects.get(pk=id)
            room.delete()
        return redirect("/rooms/")


def room_modify(request, id):
    if request.method == 'GET':
        context = {'room':Room.objects.get(pk=id)}
        return render(request, "modify_room.html", context)
    else:
        room = Room.objects.get(id=id)
        name = request.POST.get("name")
        capacity = request.POST.get("capacity")
        capacity = int(capacity) if capacity else 0
        projector = request.POST.get("projector") == "on"
        if not name:
            return render(request, "modify_room.html", context={"room": room, "error": "Enter new name"})
        if capacity <= 0:
            return render(request, "modify_room.html", context={"room": room, "error": "Enter correct capacity"})
        if name != room.name and Room.objects.filter(name=name).first():
            return render(request, "modify_room.html", context={"room": room, "error": "This Room already exist"})
        room.name = name
        room.capacity = capacity
        room.projector_availability = projector
        room.save()
        return redirect("/rooms/")



class ReservationView(View):
    def get(self, request, id):
        return render(request, 'reservation.html', {'room':Room.objects.get(id=id)})
    def post(self, request, id):
        room_id = Room.objects.get(pk=id)
        date = request.POST.get('reservation_date')
        comment = request.POST.get('comment')
        reservations = room_id.roomreservation_set.filter(date__gte=str(datetime.date.today())).order_by('date')
        if RoomReservation.objects.filter(room_id=room_id, date=date):
            return render(request, 'reservation.html', context={'room':room_id, "error":"Room is already booked this day"})
        if date < str(datetime.date.today()):
            return render(request, 'reservation.html', context={"room":room_id, "error":"Can't book in past!"})
        RoomReservation.objects.create(room_id=room_id, date=date, comment=comment)
        return redirect("/rooms/")

class RoomDetailsView(View):
    def get(self, request, id):
        room = Room.objects.get(id=id)
        reservations = room.roomreservation_set.filter(date__gte=str(datetime.date.today())).order_by('date')
        return render(request, "room_details.html", context={"room": room, "reservations": reservations})


class SearchView(View):
    def get(self, request):
        name = request.GET.get("name")
        capacity = request.GET.get("capacity")
        capacity = int(capacity) if capacity else 0
        projector = request.GET.get("projector") == "on"

        rooms = Room.objects.all()
        if projector:
            rooms = rooms.filter(projector_availability=projector)
        if capacity:
            rooms = rooms.filter(capacity__gte=capacity)
        if name:
            rooms = rooms.filter(name__icontains=name)

        for room in rooms:
            reservation_dates = [reservation.date for reservation in room.roomreservation_set.all()]
            room.reserved = str(datetime.date.today()) in reservation_dates

        return render(request, "rooms.html", context={"rooms": rooms, "date": datetime.date.today()})
