

export async function getMessages(messageType) {
    const url = `/api/msgs/retrieve/${messageType}/`;
    const response = await fetch(url, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Credentials': 'include',
        },
    });

    if (response.ok) {
        const messages = await response.json();
        console.log(`Messages of type ${messageType}:`, messages);
        return messages;
    }
    else {
        console.error('Failed to get messages:', response.status, response.statusText);
    }
}


export async function createMessage(messageType, content) {
    const url = '/api/msgs/create/';
    const csrfToken = getCsrfToken();
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({
            message_type: messageType,
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


export async function deleteMessage(messageType) {
    const url = `/api/msgs/delete/${messageType}/`;
    const csrfToken = getCsrfToken();

    try {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            credentials: 'include',
        });

        if (response.ok) {
            console.log('Message deleted successfully');
        }
        else {
            console.error('Failed to delete message:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error while deleting message:', error);
    }
}


function getCsrfToken() {
  const csrfToken = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1];

  if (!csrfToken) {
    console.error('CSRF token not found!');
    return '';
  }
  return csrfToken;
}



