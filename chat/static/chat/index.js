document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("#room-selection").forEach(function (button) {
        button.onclick = function() {
            var roomID = button.value
            window.location.pathname = roomID + "/";
        }
    });
});
