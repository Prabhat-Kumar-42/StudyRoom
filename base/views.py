from django.shortcuts import render
from django.http import request

#Create your views here.

rooms = [
    {'id':1, 'name':'Room-1'},
    {'id':2, 'name':'Room-2'},
    {'id':3, 'name':'Room-3'},
    {'id':4, 'name':'Room-4'},
]

def home(request):
    context = {'rooms': rooms}
    return render(request, 'base/home.html', context)

def room(request, pk):
    requested_room = None
    for room in rooms:
        if room['id'] == int(pk):
            requested_room = room
    context = {'room': requested_room}
    return render(request, 'base/room.html', context)
