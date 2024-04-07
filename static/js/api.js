function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let ip = null;
let chatSocket = null;
let ipInput = document.getElementById('ip');
let runPingBtn = document.getElementById('runPing');
if (ipInput && runPingBtn) {
    runPingBtn.addEventListener('click', function (e) {
        ip = ipInput.value;

        let taskResults = document.getElementById('taskResults');
        let currentScroll = null;
        let bottomScroll = null;

        if (chatSocket) {
            chatSocket.close(1000, 'normally closed');
        }
        chatSocket = new WebSocket(
            'ws://'
            + window.location.host
            + '/ws/listen/'
            + ip
            + '/'
        );

        chatSocket.onmessage = function(e) {
            currentScroll = taskResults.scrollTop;
            bottomScroll = taskResults.scrollHeight - taskResults.clientHeight;

            taskResults.innerText += e.data;

            if (currentScroll === bottomScroll) {
                taskResults.scrollTop = taskResults.scrollHeight - taskResults.clientHeight;
            }
        };

        chatSocket.onclose = function(e) {
            console.error('Socket closed unexpectedly');
        };

        fetch(
            `/api/ping/${ip}/`,
            {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
            }
        )
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log(data);
        });
    })
}
stopPingBtn = document.getElementById('stopPing');
if (stopPingBtn) {
    stopPingBtn.addEventListener('click', function (e) {
        fetch(
            `/api/ping/${ip}/`,
            {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
            }
        )
        .then((response) => {
            return response.json();
        })
        .then((data) => {
            console.log(data);
        });

        // We don't close socket connection here to receive process data
        // after terminate signal was sent.
        // Existing connection will be closed on pushing "Start ping" or
        // on tab close.
    })
}
