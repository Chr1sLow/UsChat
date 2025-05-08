import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, ChatRoom, Message

def index(request):
    if not request.user.is_authenticated:
        return render(request, "chat/login.html")

    chat_rooms = ChatRoom.objects.filter(members=request.user)

    return render(request, "chat/index.html", {
        "rooms": chat_rooms
    })


def register_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        username = request.POST["username"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "chat/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "chat/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "chat/register.html")

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "chat/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "chat/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

@login_required
def lobby(request, room_id):
    member = ChatRoom.objects.filter(members=request.user, id=room_id).exists()
    
    if not member:
        return HttpResponseRedirect(reverse("index"))
    
    room = ChatRoom.objects.get(id=room_id)

    return render(request, "chat/lobby.html", {
        "room": room,
        "owner": room.owner,
        "members": room.members.all()
    })


@csrf_exempt
@login_required
def create_chat(request):
    if request.method == "POST":
        data = json.loads(request.body)

        name = data.get("name", "")
        members = [member.strip() for member in data.get("members").split(" ")]

        recipients = []
        for member in members:
            try:
                user = User.objects.get(username=member)
                recipients.append(user)
            except User.DoesNotExist:
                return JsonResponse({
                    "error": f"User {member} does not exist."
                }, status=400)

        new_chat = ChatRoom(name=name, owner=request.user)
        new_chat.save()
        new_chat.members.add(request.user)
        for recipient in recipients:
            new_chat.members.add(recipient)
        new_chat.save()

        return JsonResponse({"message": "Chat created successfully."}, status=201)

    return render(request, "chat/create_chat.html")

def history(request, room_id):
    room = ChatRoom.objects.get(id=room_id)
    data = room.serialize()

    name = data["name"]
    owner = data["owner"]
    members = data["members"]
    messages = data["messages"]

    return JsonResponse({"name": name, "owner": owner, "members": [member for member in members], "messages": [message for message in messages]})


@csrf_exempt
@login_required
def add_members(request, room_id):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT method required."}, status=400)

    try:
        room = ChatRoom.objects.get(id=room_id)
    except ChatRoom.DoesNotExist:
        return JsonResponse({"error": "Room not found."}, status=404)
    
    data = json.loads(request.body)
    new_members = data["members"].split(" ")

    recipients = []
    for new_member in new_members:
        try:
            user = User.objects.get(username=new_member)
            recipients.append(user)
        except User.DoesNotExist:
            return JsonResponse({
                "error": f"User {new_member} does not exist."
            }, status=400)
        
    for recipient in recipients:
        if recipient not in room.members.all():
            room.members.add(recipient)
            message = Message(room=room, content=f"{recipient} has joined the group")
            message.save()
            room.messages.add(message)
    room.save()

    return HttpResponse(status=204)


def kick(request, room_id, user_id):
    room = ChatRoom.objects.get(pk=room_id)
    user = User.objects.get(pk=user_id)

    room.members.remove(user)
    room.save()

    return HttpResponse(status=204)


def profile(request, user_id):
    user = User.objects.get(pk=user_id)

    return render(request, "chat/profile.html", {
        "profile": user,
        "friend_count": user.friends.count()
    })


@login_required
def mutual_chats(request, profile_id):
    profile = User.objects.get(pk=profile_id)
    user = User.objects.get(pk=request.user.id)

    mutual_rooms = ChatRoom.objects.filter(members=profile).filter(members=user)

    return JsonResponse([room.serialize() for room in mutual_rooms], safe=False)


@login_required
def mutual_friends(request, profile_id):
    profile = User.objects.get(pk=profile_id)
    user = User.objects.get(pk=request.user.id)

    profile_friends = profile.friends.all()
    user_friends = user.friends.all()
    mutuals = profile_friends & user_friends

    return JsonResponse([friend.serialize() for friend in mutuals], safe=False)


@login_required
def friend_request(request, profile_id):
    user = User.objects.get(pk=request.user.id)
    profile = User.objects.get(pk=profile_id)

    user.sent_friend_requests.add(profile)
    profile.recieved_friend_requests.add(user)
    user.save()
    profile.save()

    return HttpResponseRedirect(f"/profile/{profile.id}")


@login_required
def recieved_requests(request):
    user = User.objects.get(pk=request.user.id)
    requests = user.recieved_friend_requests.all()

    return JsonResponse([requester.serialize() for requester in requests])


@login_required
def accept_request(request, profile_id):
    user = User.objects.get(pk=request.user.id)
    profile = User.objects.get(pk=profile_id)

    user.friends.add(profile)
    user.recieved_friend_requests.remove(profile)
    user.save()
    profile.friends.add(user)
    profile.sent_friend_requests.remove(user)
    profile.save()

    return HttpResponse(status=204)


@login_required
def delete_room(request, room_id):
    room = ChatRoom.objects.get(pk=room_id)
    room.delete()

    return HttpResponse(status=204)


@login_required
def leave_room(request, room_id):
    room = ChatRoom.objects.get(pk=room_id)
    user = User.objects.get(pk=request.user.id)
    room.members.remove(user)

    return HttpResponse(status=204)