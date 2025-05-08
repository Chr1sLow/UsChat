document.addEventListener("DOMContentLoaded", function () {
    const profile_id = document.querySelector("#profile-id").value;

    if (document.querySelector("#mutual-chats-button")) {
        document.querySelector("#mutual-chats-button").onclick = function () {
            mutual_chats(profile_id);
        };
    }

    if (document.querySelector("#mutual-friends-button")) {
        document.querySelector("#mutual-friends-button").onclick = function () {
            mutual_friends(profile_id);
        };
    }

    if (document.querySelector("#friends-button")) {
        document.querySelector("#friends-button").onclick = function () {
            friends(profile_id);
        };
    }

    if (document.querySelector("#friend-requests-log")) {
        document.querySelector("#friend-requests-log").onclick = function () {
            friend_requests(profile_id);
        };
    }

    if (document.querySelector("#accept-request")) {
        document.querySelector("#accept-request").onclick = function () {
            accept_request(profile_id);
        };
    }

    document.querySelector("#content").addEventListener("click", (event) => {
        if (event.target && event.target.id === "friend-selection") {
            var friendID = event.target.value;
            window.location.pathname = "profile/" + friendID;
        } else if (event.target && event.target.id === "room-selection") {
            var roomID = event.target.value;
            window.location.pathname = roomID + "/";
        }
    });
});

function mutual_chats(profile_id) {
    if (document.querySelector("#mutual-friends").style.display != "none") {
        document.querySelector("#mutual-friends").style.display = "none";
    }

    document.querySelector("#mutual-chats").innerHTML = "";
    document.querySelector("#mutual-chats").style.display = "flex";

    fetch(`/mutual_chats/${profile_id}`)
        .then((response) => response.json())
        .then((chats) => {
            console.log(chats);

            for (let i = 0; i < chats.length; i++) {
                let chat = chats[i];

                document.querySelector("#mutual-chats").innerHTML += `
                <button id="room-selection" value="${chat.id}">
                    <p id="room-selection-name">${chat.name}</p>
                    <p id="member-count">Members: ${chat.members.length}</p>
                </button>`;
            }

            document.querySelectorAll("#room-selection").forEach(function (button) {
                button.onclick = function () {
                    var roomID = button.value;
                    window.location.pathname = roomID + "/";
                };
            });
        });
}

function mutual_friends(profile_id) {
    if (document.querySelector("#mutual-chats").style.display != "none") {
        document.querySelector("#mutual-chats").style.display = "none";
    }

    document.querySelector("#mutual-friends").innerHTML = "";
    document.querySelector("#mutual-friends").style.display = "flex";

    fetch(`/mutual_friends/${profile_id}`)
        .then((response) => response.json())
        .then((friends) => {
            for (let i = 0; i < friends.length; i++) {
                let friend = friends[i];

                document.querySelector("#mutual-friends").innerHTML += `
                <button id="friend-selection" value=${friend.id}>${friend.username}</button>
                `;
            }

            document.querySelectorAll("#friend-selection").forEach(function (button) {
                button.onclick = function () {
                    var friendID = button.value;
                    window.location.pathname = "profile/" + friendID;
                };
            });
        });
}

// keep track of whether the friends list are displayed or not
let friends_displayed = false;
function friends(profile_id) {
    if (friends_displayed) {
        document.querySelector("#friends-list").style.display = "none";
        friends_displayed = false;
    } else {
        document.querySelector("#friends-list").style.display = "flex";
        friends_displayed = true;
    }
}

// keep track of whether the friend requests are displayed or not
let requests_displayed = false;
function friend_requests(profile_id) {
    if (requests_displayed) {
        document.querySelector("#friend-requests").style.display = "none";
        requests_displayed = false;
    } else {
        document.querySelector("#friend-requests").style.display = "flex";
        requests_displayed = true;
    }
}

function accept_request(profile_id) {
    fetch(`/accept_request/${profile_id}`).then(() => {
        window.location.reload();
    });
}
