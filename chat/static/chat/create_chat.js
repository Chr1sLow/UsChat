document.addEventListener("DOMContentLoaded", function () {
    document.querySelector("#create-chat-form").onsubmit = function (event) {
        event.preventDefault()
        const name = document.querySelector("#chat-name").value;
        const members = document.querySelector("#chat-members").value;

        fetch("/create_chat", {
            method: "POST",
            body: JSON.stringify({
                name: name,
                members: members,
            }),
        })
            .then((response) => response.json())
            .then((result) => {
                // Print result
                console.log(result);
                window.location.href = "/";
            });
    };
});
