function editUserName() {
    let el = document.getElementById("username");
    
    el.style.display = 'none';

    let input = document.getElementById("edit-username");
    input.style.display = 'inline';
    input.focus();
    input.value = el.innerText;

}


function handleUserNameBlur() {
    
    let el = document.getElementById("edit-username");
    let formData = new FormData();
    formData.append("username", el.value)

    fetch(`update-username/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // Get CSRF token
        },
        body: formData
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            let errEl = document.getElementById("update-username-error")
            if (errEl) {
                errEl.remove()
            }
            if (data.error !== '') {
                let parentElement = document.getElementById("profile-info");
                let spanElement = document.createElement("span");
                spanElement.textContent = data.error;
                spanElement.style.color = 'red';
                spanElement.setAttribute("id", "update-username-error")
                parentElement.insertBefore(spanElement, el.nextSibling)
                el.focus();
            } else {
                el.style.display = 'none'
                let username = document.getElementById("username");
                username.innerText = el.value
                username.style.display = 'inline';
                let parts = window.location.pathname.split('/')
                parts[parts.length - 2] = el.value
                history.replaceState(null, "User Profile Page", parts.join('/'));
            }

        })
        .catch(error => {
            el.focus();
        });
}


document.addEventListener('DOMContentLoaded', function() {
    const selfUsername = _getURLSelfUsername();
    const targetUsername = _getURLTargetUsername();


    const followButton = document.getElementById('follow-btn');
    if (followButton) {
        followButton.addEventListener('click', function() {
            const selfUsername = _getURLSelfUsername();
            const targetUsername = _getURLTargetUsername();

            // Todo - Check if they are already friends, if not then continue the follow process:
            let areFriends = true;
            fetch(`/api/user/${selfUsername}/anyRelations/${targetUsername}/`)
                .then(relationResponse => {
                    if (!relationResponse.ok) {
                        throw new Error('Network response was not ok.');
                    }
                    return relationResponse.json();
                })
                .then(relations => {
                    areFriends = relations["already_friend"];
                    if (areFriends) {
                        alert("You are already friends!!");
                    }
                    else {
                        // Todo - For `USER_SELF`, set `USER_TARGET` as a following of `USER_SELF`:
                        fetch(`/api/user/${selfUsername}/followerOf/${targetUsername}/`, {
                            method: 'POST',
                            headers: {
                                'X-CSRFToken': getCookie('csrftoken'),
                                'Content-Type': 'application/json'
                            }
                        })
                            .then(response => {
                                if (response.ok) {
                                    followButton.style.display = 'none';

                                    // Todo - For `USER_TARGET`, set `USER_SELF` as a follower of `USER_TARGET`:
                                    fetch(`/api/user/${targetUsername}/following/${selfUsername}/`, {
                                        method: 'POST',
                                        headers: {
                                            'X-CSRFToken': getCookie('csrftoken'),
                                            'Content-Type': 'application/json'
                                        }
                                    })
                                        .then(response => {
                                            if (response.ok) {
                                                alert("Follow Success!");
                                                // Todo - For BOTH, if the two are following each other and being followed by each other,
                                                //  then activate the “friend mechanism”, remove their following & follower relations but
                                                //  keep a friend relation between them:
                                                fetch(`/api/user/${selfUsername}/anyRelations/${targetUsername}/`)
                                                    .then(relationResponse => {
                                                        if (relationResponse.ok) {
                                                            return relationResponse.json()
                                                        }
                                                    })
                                                    .then(relations => {
                                                        let isFriend = relations["mutual_follow"]
                                                        if (isFriend) {
                                                            // Todo - If relationships are valid, then process the “friend mechanism”:
                                                            fetch(`/api/user/${selfUsername}/friend/${targetUsername}/`, {
                                                                method: 'POST',
                                                                headers: {
                                                                    'X-CSRFToken': getCookie('csrftoken'),
                                                                    'Content-Type': 'application/json'
                                                                }
                                                            })
                                                                .then(relationResponse => {
                                                                    if (relationResponse.ok) {
                                                                        alert("You are friends now!!")
                                                                        return relationResponse.json()
                                                                    }
                                                                })
                                                                .catch(error => console.error('Error:', error));
                                                        }
                                                    })
                                                    .catch(error => console.error('Error:', error));
                                            }
                                        })
                                        .catch(error => console.error('Error:', error));
                                } else {
                                    alert("Already Followed.");
                                }
                            })
                            .catch(error => console.error('Error:', error));
                    }
                })
                .catch(error => {
                    console.error('There has been a problem with your fetch operation:', error);
                });
        });
    }
});



document.addEventListener('DOMContentLoaded', () => {
    const recentPostsContainer = document.getElementById('recent-posts');
    const username = recentPostsContainer.getAttribute('data-username');
    
    console.log('Username:', username);
    fetch(`/api/user/${username}/posts`)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (Array.isArray(data.posts)) {
                data.posts.forEach(post => {
                    let postElement = document.createElement('div');
                    postElement.className = 'post';

                    const postLink = document.createElement('a');
                    postLink.href = `/posts/${post.id}`;
                    postLink.className = 'post-link';

                    const datePosted = new Date(post.date_posted);
                    const formattedDate = `${datePosted.getFullYear()}-${datePosted.getMonth() + 1}-${datePosted.getDate()}`;
                    
                    const contentHTML = `
                        <div class="content">
                        ${post.image ? `<img src="${post.image}" alt="" width="120" height="120"/>` : ''}
                            <div class="post-title">${post.title}
                            ${post.visibility === 'FRIENDS' ? '<ion-icon name="people" style="padding: 0 10px"></ion-icon>' : ''}
                            ${post.visibility === 'PRIVATE' ? '<ion-icon name="eye-off" style="padding: 0 10px"></ion-icon>' : ''}
                            </div>
                            <div class="post-time">${formattedDate}</div>
                            <p class="post-content">${post.content}</p>
                        </div>
                    `;

                    const interactionHTML = `
                        <div class="interact-container">
                            <button id="share-${post.id}" type="button" data-post-id="${post.id}">
                                <ion-icon size="small" name="share-outline" style="margin-right: 8px;"></ion-icon>
                                Share <span class="share-count">${post.share_count}</span>
                            </button>
                            <button id="comment-${post.id}" type="button" data-post-id="${post.id}">
                                <ion-icon size="small" name="chatbox-ellipses-outline" style="margin-right: 8px;">
                                </ion-icon>
                                ${post.comment_count > 0 ? '' : 'Comment'} 
                                <span class="comment-count">${post.comment_count > 0 ? post.comment_count: ''}
                                </span>
                            </button>
                            <button id="like-${post.id}" type="button" data-post-id="${post.id}"> 
                                <ion-icon size="small" name="heart-outline" style="margin-right: 8px;">
                                </ion-icon>
                                ${post.likes_count > 0 ? '' : 'Like'}
                                <span class="like-count">${post.likes_count > 0 ? post.likes_count : ''}</span>
                            </button>
                        </div>
                    `;

                    postLink.innerHTML = contentHTML;
                    postElement.appendChild(postLink);
                    postElement.innerHTML += interactionHTML;
                    recentPostsContainer.appendChild(postElement);

                    
                });
            } else {
                console.error('Error: Expected an array of posts');
                recentPostsContainer.innerHTML = '<p>Error loading posts.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching posts:', error);
            recentPostsContainer.innerHTML = '<p>Error loading posts.</p>';
        });
});


function _getURLTargetUsername() {
    const pathSections = window.location.pathname.split('/').filter(Boolean);
    return pathSections[pathSections.length - 1];
}

function _getURLSelfUsername() {
    const pathSections = window.location.pathname.split('/').filter(Boolean);
    return pathSections[pathSections.length - 2];
}

function _getRelationAnalysis(relationResponse) {
    relationResponse = relationResponse.json()
    console.log('Relationship data:', relationResponse);
    return relationResponse.get("mutual_follow")
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