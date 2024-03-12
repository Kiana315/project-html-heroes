'use strict';

document.addEventListener('DOMContentLoaded', function () {
    const moreOptionsButton = document.getElementById('more-options-button');
    const optionsContainer = document.getElementById('options-container');
    const likeButton = document.getElementById('like-button');
    const likeCountElement = document.getElementById('like-count');
    const postContainer = document.querySelector('.post-container');
    const postId = postContainer.getAttribute('data-post-id');
    const commentButton = document.getElementById('comment-button');
    const commentForm = document.getElementById('comment-form');
    const submitCommentButton = document.getElementById('submit-comment');
    const commentInput = document.getElementById('comment-input');
    const shareButton = document.getElementById('share-button');
    var shareModal = document.getElementById('shareModal');
    // var closeSpan = document.getElementsByClassName('close_share');
    var confirmShare = document.getElementById('confirmShare');
    var shareText = document.getElementById('shareText');

    checkLikeStatusAndUpdateIcon(postId);

    if (moreOptionsButton) {
        moreOptionsButton.addEventListener('click', function () {
            if (optionsContainer.style.display === 'none') {
                optionsContainer.style.display = 'block';
            } else {
                optionsContainer.style.display = 'none';
            }
        });
    }

    if (likeButton) {
        likeButton.addEventListener('click', function () {
            // const likeCount = parseInt(likeCountElement.textContent, 10);

            console.log('Like button clicked for post:', postId);

            fetch(`/api/posts/${postId}/likes/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken') // Get CSRF token
                },
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    checkLikeStatusAndUpdateIcon(postId);
                })
                .then(data => {
                    fetchLikes();
                    // likeCountElement.textContent = data.likes_count;
                    likeButton.classList.add('liked');
                })
                .catch(error => {
                    console.error('There was a problem with the fetch operation:', error);
                });
        });
    }

    if (commentButton) {
        fetchComments();
        commentButton.addEventListener('click', function () {
            commentForm.style.display = 'block'; // Show the comment form
        });

        // Event listener for submitting a comment
        submitCommentButton.addEventListener('click', function () {
            const commentText = commentInput.value.trim();

            if (commentText === '') {
                alert('Please enter a comment.');
                return;
            }

            // Proceed with submitting the comment
            fetch(`/api/posts/${postId}/comments/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({comment_text: commentText})
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
                    }
                })
                .then(() => {
                    fetchComments();
                    commentInput.value = ''; // Clear the input field
                    commentForm.style.display = 'none'; // Hide the comment form again
                })
                .catch(error => {
                    console.error('Error:', error);
                    console.log('Error message:', error.message);
                    alert(error.message);
                });
        });
    }

    if (shareButton) {
        shareButton.addEventListener('click', function () {
            shareModal.style.display = "block";
        });
    }


    // when user clicks the outside of the model, close the model
    window.onclick = function (event) {
        if (event.target == shareModal) {
            shareModal.style.display = "none";
        }
    }

    confirmShare.onclick = function () {
        // type thoughts of the post
        var text = shareText.value;

        fetch(`/api/posts/${postId}/share/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({text: text})
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    console.log('Post shared successfully', data.post_id);
                    showNotification('Post shared successfully!');
                    // Update UI design to see repost style
                } else {
                    console.error('Failed to share the post');
                    showNotification('Failed to share the post, please try again later!');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Failed to share the post, please try again later!');
            });

        shareModal.style.display = "none";
        shareText.value = '';
    }


});

function checkLikeStatusAndUpdateIcon(postId) {
    fetch(`/api/posts/${postId}/check-like/`)
        .then(response => response.json())
        .then(data => {
            updateLikeIcon(data.has_liked);
        })
        .catch(error => console.error('Error:', error));
}

function updateLikeIcon(isLiked) {
    const likeIcon = document.getElementById('like-icon');

    if (isLiked) {
        likeIcon.setAttribute('name', 'heart');
        likeIcon.style.color = 'red';
    } else {
        likeIcon.setAttribute('name', 'heart-outline');
    }
}

function fetchLikes() {
    const postContainer = document.querySelector('.post-container');
    if (!postContainer) {
        console.log('Post container not found, skipping likes fetch.');
        return;
    }

    const postId = postContainer.getAttribute('data-post-id');
    if (!postId) {
        console.error('No post ID found for fetching likes.');
        return;
    }

    fetch(`/api/posts/${postId}/likes/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            updateLikesDisplay(data.length);
        })
        .catch(error => {
            console.error('Error fetching likes:', error);
        });
}

function updateLikesDisplay(likesCount) {
    console.log('Updating likes count:', likesCount);
    const likesCountElement = document.getElementById('like-count');
    if (likesCountElement) {
        likesCountElement.textContent = likesCount;
    }
}

function fetchComments() {
    const postContainer = document.querySelector('.post-container');
    if (!postContainer) {
        console.log('Post container not found, skipping comments fetch.');
        return;
    }

    const postId = postContainer.getAttribute('data-post-id');
    if (!postId) {
        console.error('No post ID found for fetching comments.');
        return;
    }

    fetch(`/api/posts/${postId}/comments/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}, statusText: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            renderComments(data);
        })
        .catch(error => {
            console.error('Error:', error);
            console.log('Error message:', error.message);
            alert(error.message);
        });
}

function renderComments(comments) {
    const commentsContainer = document.getElementById('comments-container');
    commentsContainer.innerHTML = '';

    comments.forEach(comment => {
        // Create Content Container
        const commentElement = document.createElement('div');
        commentElement.classList.add('comment');

        const avatarElement = document.createElement('img');
        avatarElement.src = comment.commenter_avatar_url;
        avatarElement.alt = 'User Avatar';
        avatarElement.classList.add('comment-avatar');

        // add username
        const commenterNameElement = document.createElement('h5');
        commenterNameElement.textContent = comment.commenter_username;
        commenterNameElement.classList.add('commenter-name');

        // add comment text
        const commentTextElement = document.createElement('p');
        commentTextElement.textContent = comment.comment_text;
        commentTextElement.classList.add('comment-text');

        // append username, comment text, and
        commentElement.appendChild(avatarElement);
        commentElement.appendChild(commenterNameElement);
        commentElement.appendChild(commentTextElement);

        commentsContainer.appendChild(commentElement);
    });
}


function deletePost(button) {
    const postId = button.getAttribute('data-post-id');
    if (confirm("Are you sure you want to delete this post?")) {
        fetch(`/api/posts/${postId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        }).then(response => {
            if (response.status === 204) {
                showNotification('Post Deleted.');
                setTimeout(function () {
                    window.history.back();
                }, 1000);


            } else {
                alert("Something went wrong.");
            }
        }).catch(error => console.error('Error:', error));
    }
}

function showNotification(message) {
    console.log('showNotification called with message:', message);
    var notification = document.getElementById('notification');
    console.log(notification);
    notification.textContent = message;
    notification.style.display = 'block';

    // Hide the notification after 3 seconds
    setTimeout(function () {
        console.log('Hiding notification');
        notification.style.display = 'none';
    }, 3000);
}

function closeShareModal() {
    shareModal.style.display = 'none';
}

function redirectProfile() {
    var el = document.getElementById("userName")
    var currentUser = document.body.getAttribute('data-current-user');
    window.location = `/profile/${currentUser}/${el.innerText}`
    window.onload = () => {
        window.location.reload();
    }
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


// Draft Post Actions

function EditPost() {
    var postTitle = document.getElementById("postTitle")
    var postContent = document.getElementById("postContent")

    var titleInput = document.getElementById("titleInput")
    titleInput.value = postTitle.innerText
    var contentInput = document.getElementById("contentInput")
    contentInput.value = postContent.innerText

    const modal = document.getElementById("editModal");
    modal.style.display = 'block'
}

document.addEventListener('DOMContentLoaded', (event) => {
    // Get elements
    const modal = document.getElementById("editModal");
    const form = document.getElementById("editForm");
    const postId = document.getElementById("postId").innerText;

    // Click the x to close the pop-up window
    document.getElementsByClassName("close")[0].onclick = function () {
        modal.style.display = "none";
    }
    // Close pop-up window when clicking outside window
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
    form.onsubmit = function (event) {
        event.preventDefault();   //Prevent form default submission behavior

        // Create FormData Obj
        var formData = new FormData(form);
        var isDraft = event.submitter.innerText === "Save Draft"
        if (isDraft) {
            formData.append("is_draft", "true")
        }

        // Send AJAX request to server
        fetch(`/api/posts/${postId}/`, {
            method: 'PUT',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')   //Get CSRF token
            },
            credentials: 'same-origin'   // For CSRF token verification
        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    emptyPost()
                    throw new Error('Something went wrong');
                }
            })
            .then(data => {
                // After posted
                modal.style.display = "none";   //Close pop-up window
                if (isDraft) {
                    history.back();
                } else {
                    window.location = "/"
                    window.onload = function () {
                        window.reload()
                    }
                }
            })
            .catch((error) => {
                console.error('Error:', error);
                //Add error message
            });
    };
});

function sendPost() {
    var modal = document.getElementById('editModal')
    var data = {
        title: document.getElementById("postTitle").innerText,
        content: document.getElementById("postContent").innerText,
    }

    var postId = document.getElementById("postId").innerText

    // Send AJAX request to server
    fetch(`/api/posts/${postId}/`, {
        method: 'PUT',
        body: JSON.stringify(data),
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),   //Get CSRF token
            'Content-type': 'application/json'
        },
        credentials: 'same-origin'   //For CSRF token verification
    })
        .then(response => {
            if (response.ok) {
                return response.json();
            } else {
                throw new Error('Something went wrong');
            }
        })
        .then(data => {
            //After posted
            modal.style.display = "none";   //Close pop-up window
            window.location = '/'
            window.onload = function () {
                location.reload();
            };
        })
        .catch((error) => {
            console.error('Error:', error);
            // Add error message
        });
}