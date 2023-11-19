from django.shortcuts import HttpResponse, redirect, render
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Message, Room, Topic
from .forms import RoomForm, UserForm

#Create your views here.

def registerPage(request):
    page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            #user.username = user.username
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Something went wrong')
            

    context = {'page':page, 'form': form}
    return render(request, 'base/login_register.html', context)

def loginPage(request):
    page = 'login' 

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
             messages.error(request, 'User does not exists')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(home)
        else:
             messages.error(request, 'Username or Password does not exists')

    context = {'page':page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else '' #filter query
    rooms = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
            ) 
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    ).order_by('-created').order_by('-updated')

    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    requested_room = Room.objects.get(id=pk)
    room_messages = requested_room.message_set.all().order_by('created')
                                      # get all Message object of the room, here in message_set.all()
                                      # message - represents model Message, but should be written in lower case here
                                      # set - set of messages
                                      # all() - all messages
    participants = requested_room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=requested_room,
            body=request.POST.get('body')
        )
        requested_room.participants.add(request.user)
        return redirect('room', pk=requested_room.id)

    context = {'room': requested_room, 'room_messages':room_messages,
               'participants':participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messages': room_messages,
               'topics': topics}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
 
    if request.user != room.host:
        return HttpResponse('You are not authenticated to perform this operation')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name=request.POST.get('name')
        room.topic=topic
        room.decsription=request.POST.get('description')
        room.save() 
        return redirect('home')
    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not authenticated to perform this operation')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not authenticated to perform this operation')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form':form}
    return render(request, 'base/update-user.html', context)
