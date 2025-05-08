let messages_displayed = 0;
// quantity of messages loaded at a time
const quantity = 50;

document.addEventListener("DOMContentLoaded", function () {
    const roomID = JSON.parse(document.getElementById("room-id").textContent);

    console.log(roomID);
    const chatSocket = new WebSocket("ws://" + window.location.host + "/ws/" + roomID + "/");
    chat_log(roomID);

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        console.log(data);
        if (data.type === "chat") {
            document.querySelector("#chat-log").innerHTML += `
                <div id="chat-message-block">
                    <button data-message='${data["user"]}: ${data["message"]}' id="reply-button" class="btn btn-link">Reply</button>
                    <p id="message-user">${data["user"]}:</p>
                    <p id="message-content">${data["message"]}</p>
                </div>`;
            document.querySelector("#chat-log").scrollTop = document.querySelector("#chat-log").scrollHeight;
        } else if (data.type === "presence") {
            updateOnlineUsers(data.online_users);
        } else if (data.type === "typing") {
            document.querySelector("#typing-notif").innerHTML = `${data["user"]} is typing...`;
            document.querySelector("#typing-notif").style.display = "flex";
        } else if (data.type === "no_typing") {
            document.querySelector("#typing-notif").innerHTML = "";
            document.querySelector("#typing-notif").style.display = "none";
        }
    };

    chatSocket.onclose = function (e) {
        console.error("Chat socket closed unexpectedly");
    };

    const submit = document.querySelector("#chat-message-submit");
    submit.disabled = true;
    document.querySelector("#chat-message-input").focus();
    document.querySelector("#chat-message-input").onkeyup = function (e) {
        if (document.querySelector("#chat-message-input").value.length > 0) {
            submit.disabled = false;
            chatSocket.send(
                JSON.stringify({
                    type: "typing",
                })
            );
            if (e.key === "Enter") {
                // enter, return
                document.querySelector("#chat-message-submit").click();
            }
        } else {
            if (chatSocket.readyState === 1) {
                chatSocket.send(
                    JSON.stringify({
                        type: "no_typing",
                    })
                );
            }
            submit.disabled = true;
        }
    };

    document.querySelector("#chat-message-submit").onclick = function (e) {
        const messageInputDom = document.querySelector("#chat-message-input");
        const message = messageInputDom.value;
        chatSocket.send(
            JSON.stringify({
                type: "message",
                message: message,
            })
        );
        messageInputDom.value = "";
        submit.disabled = true;
    };

    document.querySelector("#add-members").onclick = function () {
        add_member(roomID);
    };

    document.querySelectorAll("#kick").forEach(function (element) {
        element.addEventListener("click", function (event) {
            document.querySelector(`#member${event.target.dataset.userid}`).remove();
        });
    });

    document.querySelector("#chat-log").addEventListener("click", (event) => {
        if (event.target && event.target.id === "reply-button") {
            reply(event.target.dataset.message);
        }
    });

    if (document.querySelector("#delete-chat")) {
        document.querySelector("#delete-chat").onclick = function () {
            delete_chat(roomID);
        };
    }
    if (document.querySelector("#leave-chat")) {
        document.querySelector("#leave-chat").onclick = function () {
            leave_chat(roomID);
        };
    }
});

function updateOnlineUsers(online_users) {
    // change color of member to gray when offline
    document.querySelectorAll("#members .dropdown a").forEach(function (element) {
        element.style.color = "gray";
    });

    // change color of member to green when online
    for (let i = 0; i < online_users.length; i++) {
        let user = online_users[i];
        document.querySelector(`#member${user["id"]} a`).style.color = "#4eb300";
    }
}

function chat_log(room_id) {
    fetch(`/history/${room_id}`)
        .then((response) => response.json())
        .then((room) => {
            console.log(room);

            // get the latest 25 messages
            for (let i = Math.max(room["messages"].length - quantity, 0); i < room["messages"].length; i++) {
                let message = room["messages"][i];

                document.querySelector("#chat-log").innerHTML += `
                <div id="chat-message-block">
                    <button data-message='${message["user"]}: ${message["content"]}' id="reply-button" class="btn btn-link">Reply</button>
                    <p id="message-user">${message["user"]}:</p>
                    <p id="message-content">${message["content"]}</p>
                </div>`;
            }
            document.querySelector("#chat-log").scrollTop = document.querySelector("#chat-log").scrollHeight;

            let chatlogElement = document.querySelector("#chat-log");
            chatlogElement.onscroll = () => {
                // retrieve older messages when the user reaches the top
                if (chatlogElement.scrollTop === 0) {
                    setTimeout(() => {
                        load(chatlogElement, room, room["messages"].length);
                    });
                }
            };
        });
}

function load(chatlogElement, room, total_messages) {
    messages_displayed += quantity;
    let end = total_messages - messages_displayed;
    let start = Math.max(end - quantity, 0);
    console.log(room);
    let previous_height = chatlogElement.scrollHeight;

    // load the older messages
    for (let i = end; i > start; i--) {
        let current_messages = document.querySelector("#chat-log").innerHTML;
        let message = room["messages"][i];

        document.querySelector("#chat-log").innerHTML =
            `
        <div id="chat-message-block">
            <p id="chat-message">${message["user"]}: ${message["content"]}</p>
            <button data-message='${message["user"]}: ${message["content"]}' id="reply-button" class="btn btn-link">Reply</button>
        </div>` + current_messages;
    }
    let new_height = chatlogElement.scrollHeight;

    chatlogElement.scrollTop = new_height - previous_height;
}

function add_member(room_id) {
    document.querySelector("#chat-room-view").style.display = "none";
    document.querySelector("#settings").style.display = "none";
    document.querySelector("#add-members-view").style.display = "flex";

    document.querySelector("#add-cancel").onclick = function () {
        document.querySelector("#chat-room-view").style.display = "flex";
        document.querySelector("#settings").style.display = "flex";
        document.querySelector("#add-members-view").style.display = "none";
    };

    document.querySelector("#add-member-form").onsubmit = function () {
        let new_members = document.querySelector("#chat-members").value;

        fetch(`/add_members/${room_id}`, {
            method: "PUT",
            body: JSON.stringify({
                members: new_members,
            }),
        }).then(() => {
            window.location.reload();
        });

        return false;
    };
}

function reply(message) {
    console.log(message);
    document.querySelector("#chat-message-input").value = `Replying to "${message}": `;
}

function delete_chat(room_id) {
    document.querySelector("#chat-room-view").style.display = "none";
    document.querySelector("#settings").style.display = "none";
    document.querySelector("#remove-room-view").style.display = "block";

    document.querySelector("#delete-cancel").onclick = function () {
        document.querySelector("#chat-room-view").style.display = "flex";
        document.querySelector("#settings").style.display = "flex";
        document.querySelector("#remove-room-view").style.display = "none";
    };

    document.querySelector("#delete-confirm").onclick = function () {
        fetch(`/delete_chat/${room_id}`).then(() => {
            window.location.pathname = "";
        });
    };
}

function leave_chat(room_id) {
    document.querySelector("#chat-room-view").style.display = "none";
    document.querySelector("#settings").style.display = "none";
    document.querySelector("#leave-room-view").style.display = "block";

    document.querySelector("#leave-cancel").onclick = function () {
        document.querySelector("#chat-room-view").style.display = "flex";
        document.querySelector("#settings").style.display = "flex";
        document.querySelector("#leave-room-view").style.display = "none";
    };

    document.querySelector("#leave-confirm").onclick = function () {
        fetch(`/leave_chat/${room_id}`).then(() => {
            window.location.pathname = "";
        });
    };
}
