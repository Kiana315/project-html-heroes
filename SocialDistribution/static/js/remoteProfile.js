document.addEventListener('DOMContentLoaded', async function() {
    let selfUsername;
    const response = await fetch('/api/get-self-username/');
    if (response.ok) {
        const data = await response.json();
        selfUsername = data.username;
    }
    const remoteNodename = _getURLRemoteNodename();
    const remoteUsername = _getURLRemoteUsername();

    const FRAcceptURL = `${window.location.protocol}/${window.location.hostname}/accept-remote-follow/${remoteNodename}/${selfUsername}/${remoteUsername}/`;
    const FRRejectURL = `${window.location.protocol}/${window.location.hostname}/reject-remote-follow/${remoteNodename}/${selfUsername}/${remoteUsername}/`;
    const urlsJSON = {
        click_to_accept_the_remote_follow_request: FRAcceptURL,
        click_to_reject_the_remote_follow_request: FRRejectURL
    };
    console.log("FRAcceptURL", FRAcceptURL);
    console.log("FRRejectURL", FRRejectURL);

    const followButton = document.getElementById('follow-btn');
    const unfollowButton = document.getElementById('unfollow-btn');
    const relationInstruction = document.getElementById('relation');

    // todo
    followButton.style.display = "none";
    unfollowButton.style.display = "none";
    fetch(`remote-check-follower/${remoteNodename}/${remoteUsername}/`)
        .then(relationResponse => {
            if (!relationResponse.ok) {
                alert("Error in checking relationship.")
            }
            return relationResponse.json();
        })
        .then(relations => {
            if (relations["is_follower"]) {
                relationInstruction.textContent = `- You Are Following Remote User ${remoteUsername} from ${remoteNodename} -`;
                followButton.style.display = "none";
                unfollowButton.style.display = "inline";
            }
            else {
                relationInstruction.textContent = `- Hi, I'm ${remoteUsername} from ${remoteNodename}, Nice To Meet U -`;
                followButton.style.display = "inline";
                unfollowButton.style.display = "none";
            }
        });

    if (followButton) {
        followButton.addEventListener('click', function() {

        });
    }

    if (unfollowButton) {
        unfollowButton.addEventListener('click', function() {

        });
    }


});


// Load friend list
document.addEventListener('DOMContentLoaded', () => {
    const friendListContainer = document.getElementById('friendList');
    const username = _getURLRemoteUsername();

    fetch(`/api/user/${username}/friends/`)
        .then(response => response.json())
        .then(friendships => {
            // console.log(friendships.length);
            if (friendships.length === 0) {
                friendListContainer.style.display = 'none';
                return;
            }

            friendships.forEach(friendship => {

                let friend;
                if (friendship.user1.username === username) {
                    friend = friendship.user2;
                }
                else {
                    return;
                }
                console.log(friend);

                let friendElement = document.createElement('div');
                friendElement.className = 'friend-info';

                friendElement.innerHTML = `
                <div class="friend-avatar">
                    <img src="${friend.avatar}" alt="Friend Avatar">
                </div>
                <div class="friend-name">
                    <a href="/profile/${username}/${friend.username}">${friend.username}</a> 
                </div>
                `;

                friendListContainer.appendChild(friendElement);
            });
        })
        .catch(error => {
            console.error('Error fetching friends:', error);
            friendListContainer.innerHTML = '<p>Error loading friends.</p>';
        });
});


function _getURLRemoteUsername() {
    const pathSections = window.location.pathname.split('/').filter(Boolean);
    return pathSections[pathSections.length - 1];
}

function _getURLRemoteNodename() {
    const pathSections = window.location.pathname.split('/').filter(Boolean);
    return pathSections[pathSections.length - 2];
}


function _getRelationAnalysis(relationResponse) {
    relationResponse = relationResponse.json()
    console.log('Relationship data:', relationResponse);
    return relationResponse.get("mutual_follow")
}

async function _getRemoteUserOPENAPIS(serverNodeName, username) {
    const encodedServerNodeName = encodeURIComponent(serverNodeName);
    const encodedUsername = encodeURIComponent(username);

    const url = `/api/getRemoteUserOPENAPIS/${encodedServerNodeName}/${encodedUsername}/`;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log("data", data);
        return data;
    } catch (error) {
        console.error('Error fetching remote user data:', error);
    }
}

async function createRemoteMessage(remoteMsgOpenAPI, messageType, content, origin = "SYS") {
    const csrfToken = getCsrfToken();
    const response = await fetch(remoteMsgOpenAPI, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            message_type: messageType,
            origin: origin,
            content: content,
        }),
    });

    if (response.ok) {
        const data = await response.json();
        console.log('Message created successfully:', data);
    }
    else {
        const error = await response.json();
        console.error('Failed to create message:', response.status, response.statusText, error);
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
