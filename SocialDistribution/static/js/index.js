'use strict';

import {formatDate} from "./common.js";

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
                const formattedDate = formatDate(datePosted)
                
                const userInfoHTML = `
                    <div class="user-info">
                        <img src="${post.avatar}" alt="profile avatar" class="user-avatar">
                        <div class="username">${post.username || 'Unknown User'}</div>
                        <div class="post-time">${formattedDate}</div>
                        <div class="corner-icon">
                            ${post.content_type === 'COMMONMARK' ? '<ion-icon name="logo-markdown" style="padding: 0 10px; position: relative; margin-left: auto;"></ion-icon>' : ''}
                        </div>
                    </div>
                `;

                const contentHTML = `
                    <div class="content">
                        <div class="title">${post.title}</div>
                        <p class="post-content">${post.content}</p>
                        ${createImagesHTML(post.image_data)}
                    </div>
                `;
                // <img src="${post.image_data}>
                const interactionHTML = `
                    <div class="interact-container">
                        <!-- <button id="share-${post.id}" type="button" data-post-id="${post.id}">
                            <ion-icon size="small" name="share-outline" style="margin-right: 8px;"></ion-icon>
                            Share <span class="share-count">${post.share_count}</span>
                        </button> -->
                        <button id="comment-${post.id}" type="button" data-post-id="${post.id}">
                            <ion-icon size="small" name="chatbox-ellipses-outline" style="margin-right: 8px;">
                            </ion-icon>
                                ${post.comment_count > 0 ? '' : 'Comment'} 
                                <span class="comment-count">${post.comment_count > 0 ? post.comment_count : ''}
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
                postLink.innerHTML = userInfoHTML + contentHTML + interactionHTML;
                postElement.appendChild(postLink);
                // postElement.innerHTML += interactionHTML;
                postContainer.appendChild(postElement);

            });
        })
        .catch(error => console.error('Error:', error));
})

export function createRemotePostBlocks_self(remotePosts) {
    console.log("@ remotePosts", remotePosts);
    const postContainer = document.getElementById('post-container');
    remotePosts.forEach(post => {
        const postElement = document.createElement('div');
        postElement.className = 'post';

        const postLink = document.createElement('a');
        postLink.href = `/posts/remote/${post.author}/${post.id}`;
        postLink.className = 'post-link';

        const datePosted = new Date(post.date_posted);
        const formattedDate = formatDate(datePosted);

        const userInfoHTML = `
            <div class="user-info">
                <img src="${post.avatar}" alt="profile avatar" class="user-avatar">
                <div class="username">${post.username || 'Unknown User'}</div>
                <div class="post-time">${formattedDate}</div>
                <div class="corner-icon">
                    ${post.content_type === 'COMMONMARK' ? '<ion-icon name="logo-markdown"></ion-icon>' : ''}
                </div>
            </div>
        `;

        const contentHTML = `
            <div class="content">
                <div class="title">${post.title}</div>
                <p class="post-content">${post.content}</p>
                ${createImagesHTML(post.image_data)}
            </div>
        `;

        postLink.innerHTML = userInfoHTML + contentHTML;
        postElement.appendChild(postLink);
        postContainer.appendChild(postElement);
    });
}


export function createRemotePostBlocks_enjoy(remotePosts) {
    console.log("@ remotePosts", remotePosts);
    const postContainer = document.getElementById('post-container');
    remotePosts.forEach(post => {
        const postElement = document.createElement('div');
        postElement.className = 'post';

        const postLink = document.createElement('a');
        postLink.href = `/posts/remote/${post.author.displayName}/${post.user}`;
        postLink.className = 'post-link';

        const datePosted = new Date(post.published);
        const formattedDate = formatDate(datePosted);

        const userInfoHTML = `
            <div class="user-info">
                <img src="${post.avatar}" alt="profile avatar" class="user-avatar">
                <div class="username">${post.author.displayName || 'Unknown User'}</div>
                <div class="post-time">${formattedDate}</div>
                <div class="corner-icon">
                    ${post.content_type === 'COMMONMARK' ? '<ion-icon name="logo-markdown"></ion-icon>' : ''}
                </div>
            </div>
        `;

        const contentHTML = `
            <div class="content">
                <div class="title">${post.title}</div>
                <p class="post-content">${post.content}</p>
                ${createImagesHTML(post.image_data)}
            </div>
        `;

        postLink.innerHTML = userInfoHTML + contentHTML;
        postElement.appendChild(postLink);
        postContainer.appendChild(postElement);
    });
}



function createImagesHTML(imageDataString) {
    if (!imageDataString) return '';

    const imageDataArray = imageDataString.split(","); 
    let imagesHTML = '';

    for (let i = 1; i < imageDataArray.length; i += 2) {
        let base64Data = imageDataArray[i];
        if (base64Data.trim()) {
            imagesHTML += `<img src="data:image/jpeg;base64,${base64Data}" class="post-image" style="max-width: 100%; height: auto;">`;
        }
    }
    return imagesHTML;
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