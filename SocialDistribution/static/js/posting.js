
document.addEventListener('DOMContentLoaded', (event) => {
    // Get elements
    const textModal = document.getElementById("newTextPost");
    const imageModal = document.getElementById("newImagePost");
    const btn = document.getElementById("floating-button");
    const form = document.getElementById("newPostForm");
    const postType = document.getElementById("post-option");
    const textBtn = document.getElementById("text-post");
    const imageBtn = document.getElementById("image-post");

    // Open pop-up window when clicking floating button
    btn.addEventListener('click', function() {
        postType.style.display = "block";
    });

    textBtn.addEventListener('click', function() {
        textModal.style.display = "block";
        postType.style.display = "none";
    });
    imageBtn.addEventListener('click', function() {
        imageModal.style.display = "block";
        postType.style.display = "none";
    });

    
    window.onclick = function(event) {
        if (event.target === postType) {
            postType.style.display = "none";
        }
    }
    form.onsubmit = function(event) {
        event.preventDefault(); // Prevent form default submission behavior

        let useCommonMark = document.getElementById('content_type').checked;
        let contentType = useCommonMark ? 'COMMONMARK' : 'PLAIN';

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
            textModal.style.display = "none"; // Close pop-up window
            submitPost();

        })
        .catch((error) => {
            console.error('Error:', error);
            
        });
    };
});


// Preview image
document.addEventListener('DOMContentLoaded', (event) => {
    const imageUploadInput = document.getElementById('imageUpload');
    const previewContainer = document.getElementById('imagePreviewContainer'); 

    imageUploadInput.addEventListener('change', function(event) {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
            
            reader.onload = function(e) {
                var imgElement = document.createElement('img');
                imgElement.src = e.target.result;
                imgElement.style.width = 'auto'; 
                imgElement.style.maxWidth = '150px';
                imgElement.style.height = 'auto';
                imgElement.style.maxHeight = '150px';
                imgElement.style.marginRight = '15px'; 

                previewContainer.appendChild(imgElement); 
            }

            reader.readAsDataURL(this.files[0]); // 读取文件
        }
    });
});

// Click the x to close the pop-up window
function closeModal() {
    const textModal = document.getElementById("newTextPost");
    const imageModal = document.getElementById("newImagePost");
    imageModal.style.display = "none";
    textModal.style.display = "none";
    console.log("call close")
}

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
