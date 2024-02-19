'use strict';



document.addEventListener('DOMContentLoaded', (event) => {
    // Get elements
    const modal = document.getElementById("newPostModal");
    const btn = document.getElementById("floating-button");
    const form = document.getElementById("newPostForm");
    

    // Open pop-up window when clicking floating button
    btn.onclick = function() {
        modal.style.display = "block";
    };

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

        // Create FormData Obj
        var formData = new FormData(form);

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
                
                return response.json();
            } else {
                emptyPost()
                throw new Error('Something went wrong');
            }
        })
        .then(data => {
            // After posted
            console.log('Success:', data);            
            modal.style.display = "none"; // Close pop-up window
            submitPost();
            // Refresh the page 
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


// function showPopup() {
//     let popup = document.getElementById("popup");
//     popup.style.display = "block";
// }

function submitPost() {
    alert("Post submitted successfully, please refresh to see your post.");
}

function emptyPost() {
    alert("Please write something...");
}

// function addImage() {
//     alert("The 'Add Image' feature is not implemented in this demo.");
// }

// function tagFriends() {
//     alert("The '@ Tag Friends' feature is not implemented in this demo.");
// }

// showPopup()