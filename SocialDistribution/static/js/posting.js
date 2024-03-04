
document.addEventListener('DOMContentLoaded', (event) => {
    // Get elements
    
    const modal = document.getElementById("newPostModal");
    const btn = document.getElementById("floating-button");
    const form = document.getElementById("newPostForm");

    // Open pop-up window when clicking floating button
    btn.addEventListener('click', function() {
        modal.style.display = "block";
    });
    // Click the x to close the pop-up window
    document.getElementsByClassName("close")[0].onclick = function() {
        modal.style.display = "none";
    }
    // Close pop-up window when clicking outside window
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
    form.onsubmit = function(event) {
        event.preventDefault(); // Prevent form default submission behavior

        let useCommonMark = document.getElementById('content_type').checked;
        let contentType = useCommonMark ? 'COMMONMARK' : 'PLAIN';
        console.log("content_type", contentType);

        // Create FormData Obj
        var formData = new FormData(form);
        formData.append("content_type", contentType);
        
        if (event.submitter.innerText === "Save Draft"){
            formData.append("is_draft", "true")
        }

        // Send AJAX request to server
        fetch('/api/nps/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Get CSRF token
            },
            credentials: 'same-origin' // For CSRF token verification
        })
        .then(response => {
            if(response.ok) {
                window.location.reload();
                return response.json();
            } else {
                emptyPost()
                throw new Error('Something went wrong');
            }
        })
        .then(data => {
            // After posted
            modal.style.display = "none"; // Close pop-up window
            submitPost();

        })
        .catch((error) => {
            console.error('Error:', error);
            // Add error message
        });
    };
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
