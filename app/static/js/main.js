window.onload = function() {
    var timerElement = document.getElementById('timer');
    var timeLeft = 10;

    var timer = setInterval(function() {
        timeLeft--;
        timerElement.textContent = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(timer);
            window.location.href = '/connect';
        }
    }, 1000);
};
