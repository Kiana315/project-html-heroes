'use strict';


document.addEventListener('DOMContentLoaded', () => {
  

    fetch('/api/pps/')
        .then(response => response.json())
        .then(posts => {
            const postContainer = document.getElementById('post-container');
            posts.forEach(post => {
                const postElement = document.createElement('div');
                postElement.className = 'post';

                const postLink = document.createElement('a');
                postLink.href = `/posts/${post.id}`;
                postLink.className = 'post-link';

                const datePosted = new Date(post.date_posted);
                const formattedDate = `${datePosted.getFullYear()}-${datePosted.getMonth() + 1}-${datePosted.getDate()}`;

                const userInfoHTML = `
                    <div class="user-info">
                        <img src="${post.avatar}" alt="profile avatar" class="user-avatar">
                        <div class="username">${post.username || 'Unknown User'}</div>
                        <div class="post-time">${formattedDate}</div>
                    </div>
                `;

                const contentHTML = `
                    <div class="content">
                        <div class="title">${post.title}</div>
                        <p>${post.content}</p>
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

                // Append userInfoHTML, contentHTML, and interactionHTML to postLink instead of postElement
                postLink.innerHTML = userInfoHTML + contentHTML;
                postElement.appendChild(postLink);
                postElement.innerHTML += interactionHTML;
                postContainer.appendChild(postElement);

                
                // Event listeners for like button
                const likeButton = postElement.querySelector(`#like-${post.id}`);
                likeButton.addEventListener('click', function() {
                    console.log("like clicked",`api/posts/${post.id}/likes/`);
                    // 点赞操作的 AJAX 请求
                    // 更新点赞计数
                    fetch(`/api/posts/${post.id}/likes/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken'), 
                            'Content-Type': 'application/json'
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // 更新页面上的点赞计数
                            const likeCountSpan = postElement.querySelector(`#like-${post.id} .like-count`);
                            likeCountSpan.textContent = data.likes_count; // 假设后端返回更新后的点赞计数
                        } else {
                            // 处理错误情况
                            console.error('Error:', data.error);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                    });
                });


                // Event listeners for like button
                const commentButton = postElement.querySelector(`#comment-${post.id}`);
                commentButton.addEventListener('click', function() {
                    console.log("comment clicked");
                    // 评论操作的 AJAX 请求
                    // 更新评论计数
                });

                // commentButton.addEventListener('click', (e) => {
                //     e.stopPropagation();
                //     commentBox.style.display = commentBox.style.display === 'none' ? 'block' : 'none';
                // });
                // likeButton.addEventListener('click', (e) => {
                //     e.stopPropagation();
                //     console.log('Like button clicked for post:', post.id);
                //     fetch(`/api/posts/${post.id}/likes/`, {
                //         method: 'POST',
                //         headers: {'Content-Type': 'application/json'},
                //         body: JSON.stringify({}),
                //     })
                //     .then(response => {
                //         if (response.ok) {
                //             console.log('>> Like Sent Successfully;');
                //         } else {
                //             console.log('>> Like Sent Unsuccessfully;');
                //         }
                //     })
                //     .catch(error => console.error('Error:', error));
                // });

                // const submitCommentButton = commentBox.querySelector('.submit-comment');
                // submitCommentButton.addEventListener('click', () => {
                //     const commentText = commentBox.querySelector('.comment-text').value;
                //     console.log('Comment submitted for post:', post.id, 'Comment:', commentText);
                //     fetch(`/api/posts/${post.id}/comments/`, {
                //         method: 'POST',
                //         headers: {'Content-Type': 'application/json'},
                //         body: JSON.stringify({ text: commentText }),
                //     })
                //     .then(response => {
                //         if (response.ok) {
                //             console.log('>> Comment Sent Successfully;');
                //         } else {
                //             console.log('>> Comment Sent Unsuccessfully;');
                //         }
                //     })
                //     .catch(error => console.error('Error:', error));
                // });
            });
        })
        .catch(error => console.error('Error:', error));
})

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
