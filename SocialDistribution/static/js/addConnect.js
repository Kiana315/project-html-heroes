document.addEventListener('DOMContentLoaded', function() {
    let form = document.querySelector('.ac-container form');

    form.addEventListener('submit', function(event) {
        event.preventDefault();

        let targetHost = document.querySelector('[name="targetHost"]').value;
        let username = document.querySelector('[name="username"]').value;
        let password = document.querySelector('[name="password"]').value;

        let formData = {
            targetHost: targetHost,
            username: username,
            password: password
        };

        fetch('', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});





function getCSRFToken() {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, 'csrftoken'.length + 1) === ('csrftoken' + '=')) {
                cookieValue = decodeURIComponent(cookie.substring('csrftoken'.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}