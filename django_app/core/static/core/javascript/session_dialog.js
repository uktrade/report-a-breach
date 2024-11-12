function Counter(options) {
    var timer;
    var instance = this;
    var seconds = options.seconds || 10;
    var onUpdateStatus = options.onUpdateStatus || function () {
    };
    var onCounterEnd = options.onCounterEnd || function () {
    };

    function decrementCounter() {
        onUpdateStatus(seconds);
        if (seconds === 0) {
            stopCounter();
            onCounterEnd();
            return;
        }
        seconds--;
    }

    function startCounter() {
        clearInterval(timer);
        timer = 0;
        decrementCounter();
        timer = setInterval(decrementCounter, 1000);
    }

    function stopCounter() {
        clearInterval(timer);
    }

    return {
        start: function () {
            startCounter();
        },
        stop: function () {
            stopCounter();
        }
    }
}

function setup_session_dialog(session_expiry_seconds) {
    const dialog_element = document.getElementById("session_expiry_dialog")
    const time_remaining_element = document.getElementById('session_expiry_time_remaining');

    var countdown = new Counter({
        // number of seconds to count down
        seconds: session_expiry_seconds,

        // callback function for each second
        onUpdateStatus: function (second) {
            if (second <= 300) {
                // we are below 5 minutes, change the minutes left text and show the modal
                time_remaining_element.innerText = Math.floor(second / 60) + " minutes";

                if (second <= 60) {
                    // we only have a minute left, show the timer
                    time_remaining_element.innerText = second + " seconds";

                    if (second === 1) {
                        // 1 second left, just to fix the grammar
                        time_remaining_element.innerText = "1 second";
                    }
                }

                dialog_element.showModal();
            }
        },

        // callback function for final action after countdown
        onCounterEnd: function () {
            // session expired, reset it
            window.location.replace("/session_expired")
        }
    });
    countdown.start();

    document.getElementById("ping_session_button").addEventListener('click', () => {
        $.ajax({
            url: '/ping_session',
            type: 'GET',
            success: function (data) {
                time_remaining_element.innerText = session_expiry_seconds / 60 + " minutes";
                countdown.seconds = session_expiry_seconds;
                countdown.start()
            },
            error: function (request, error) {
                alert("Request: " + JSON.stringify(request));
            }
        });

        dialog_element.close();
    });


}
