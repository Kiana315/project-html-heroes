
document.addEventListener('DOMContentLoaded', (event) => {
    // Get elements
    var imageDatas = [];

    const textModal = document.getElementById("newTextPost");
    const imageModal = document.getElementById("newImagePost");
    const btn = document.getElementById("floating-button");
    const textForm = document.getElementById("newTextForm");
    const imageForm = document.getElementById("newImageForm");
    const postType = document.getElementById("post-option");
    const textBtn = document.getElementById("text-post");
    const imageBtn = document.getElementById("image-post");

    const imageUploadInput = document.getElementById('imageUpload');
    const previewContainer = document.getElementById('imagePreviewContainer'); 

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
        if (event.target === imageModal) {
            imageModal.style.display = "none";
        }
        if (event.target === textModal) {
            textModal.style.display = "none";
        }
    }
    
    textForm.onsubmit = function(event) {
        event.preventDefault(); // Prevent form default submission behavior

        let useCommonMark = document.getElementById('content_type').checked;
        let contentType = useCommonMark ? 'COMMONMARK' : 'PLAIN';

        // Create FormData Obj
        var formData = new FormData(textForm);
        formData.append("content_type", contentType);
        for (var pair of formData.entries()) {
            console.log(pair[0]+ ', ' + pair[1]); 
        }

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
                // emptyPost();
                throw new Error('Something went wrong');
            }
        })
        .then(data => {
            // After posted
            textModal.style.display = "none"; // Close pop-up window
            // submitPost();

        })
        .catch((error) => {
            console.error('Error:', error);
            
        });
    };

    // Handling image posts(omly images)
    imageUploadInput.addEventListener('change', function(event) {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
 
            reader.onload = function(e) {
                var imageData = e.target.result;    // Get Base64 encoded image data
                imageDatas.push(imageData);     //Add image data to the global array
                console.log("images>>>>>> ", imageDatas);
                var imgElement = document.createElement('img');
                imgElement.src = imageData;
                imgElement.style.width = 'auto'; 
                imgElement.style.maxWidth = '150px';
                imgElement.style.height = 'auto';
                imgElement.style.maxHeight = '150px';
                imgElement.style.marginRight = '15px'; 

                previewContainer.appendChild(imgElement); 

                imageForm.onsubmit = function(event) {
                    event.preventDefault(); // Prevent form default submission behavior
                
                    var formData = new FormData(imageForm);
                            
                    // Append the image data stored in the imageDatas array to the FormData object                    
                    formData.append('image_data', imageDatas);
                    
                 
                    fetch('/api/nps/', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken') 
                        },
                        credentials: 'same-origin' 
                    })
                    .then(response => {
                        if(response.ok) {
                            window.location.reload();
                            return response.json();
                        } else {
                            // emptyPost();
                            throw new Error('Something went wrong');
                            alert('Some error occurred.');
                        }
                    })
                    .then(data => {
                        imageModal.style.display = "none"; 
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                        alert('Some error occurred.');
                    });
                };
            }
            reader.readAsDataURL(this.files[0]); 
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
