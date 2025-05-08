from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register_view, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("<int:room_id>/", views.lobby, name="lobby"),
    path("create_chat", views.create_chat, name="create_chat"),
    path("kick/<int:room_id>/<int:user_id>", views.kick, name="kick"),
    path("friend_request/<int:profile_id>", views.friend_request, name="friend_request"),
    path("accept_request/<int:profile_id>", views.accept_request, name="accept_request"),

    path("history/<int:room_id>", views.history, name="history"),
    path("add_members/<int:room_id>", views.add_members, name="add_members"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("mutual_chats/<int:profile_id>", views.mutual_chats, name="mutual_chats"),
    path("mutual_friends/<int:profile_id>", views.mutual_friends, name="mutual_friends"),
    path("delete_chat/<int:room_id>", views.delete_room, name="delete_room"),
    path("leave_chat/<int:room_id>", views.leave_room, name="leave_room")
]