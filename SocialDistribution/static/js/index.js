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
                postLink.href = `/api/posts/${post.id}`;
                postLink.className = 'post-link';

                const userInfoHTML = `
                    <div class="user-info">
                        <img src="${post.author.profile_picture}" alt="profile picture" class="avatar">
                        <div class="username">${post.author.username}</div>
                    </div>
                `;

                const contentHTML = `
                    <div class="content">
                        <div class="title">${post.title}</div>
                        <p>${post.content}</p>
                    </div>
                `;

                const interactionHTML = `
                    <div class="interactions">
                        <button type="button" class="like-btn">Like</button>
                        <button type="button" class="comment-btn">Comment</button>
                    </div>
                `;

                // Append userInfoHTML, contentHTML, and interactionHTML to postLink instead of postElement
                postLink.innerHTML = userInfoHTML + contentHTML;
                postElement.appendChild(postLink);
                postElement.innerHTML += interactionHTML;
                postContainer.appendChild(postElement);

                // Event listeners for like and comment buttons
                const likeButton = postElement.querySelector('.like-btn');
                const commentButton = postElement.querySelector('.comment-btn');
                const commentBox = document.createElement('div');
                commentBox.className = 'comment-box';
                commentBox.style.display = 'none';
                commentBox.innerHTML = `
                    <textarea class="comment-text" placeholder="Add a comment..."></textarea>
                    <button type="button" class="submit-comment">Post Comment</button>
                `;

                postElement.appendChild(commentBox);

                commentButton.addEventListener('click', (e) => {
                    e.stopPropagation(); // Prevent the click from triggering the post link
                    commentBox.style.display = commentBox.style.display === 'none' ? 'block' : 'none';
                });
                likeButton.addEventListener('click', (e) => {
                    e.stopPropagation(); // Prevent the click from triggering the post link
                    console.log('Like button clicked for post:', post.id);
                    // Implement like functionality here
                });

                // Event listener for the comment submission
                const submitCommentButton = commentBox.querySelector('.submit-comment');
                submitCommentButton.addEventListener('click', () => {
                    const commentText = commentBox.querySelector('.comment-text').value;
                    console.log('Comment submitted for post:', post.id, 'Comment:', commentText);
                    // Implement comment functionality here
                });
            });
        })
        .catch(error => console.error('Error:', error));
});


/*
function createPostElement(post) {
    // 创建帖子元素
    const postDiv = document.createElement('div');
    postDiv.className = 'post';

    // 添加用户信息
    const userInfo = document.createElement('div');
    userInfo.className = 'user-info';
    userInfo.innerHTML = `
        <img src="${post.author.profile_picture}" alt="profile picture" class="avatar">
        <div class="username">${post.author.username}</div>
    `;
    postDiv.appendChild(userInfo);

    // 添加帖子内容
    const content = document.createElement('div');
    content.className = 'content';
    content.innerHTML = `<p>${post.content}</p>`;
    postDiv.appendChild(content);

    return postDiv;
}*/