'use strict';

import {
    getMessages,
    createMessage,
    deleteMessageType,
    deleteMessageID,
} from './messageOperations.js';

function clickableListItem(messages) {
    messages.forEach(function(message) {
        message.querySelector('.message-header').addEventListener('click', function() {
            message.classList.toggle('unfolded');
        });
    });
}

function clickableFilterMessages() {
    let filterForm = document.getElementById('filter-form');
    filterForm.addEventListener('submit', function(event) {
        event.preventDefault();
        let type = document.getElementById('filter').value;
        filterAndDisplayMessages(type);
    });
}

function filterAndDisplayMessages(filter) {
    let messageContainer = document.querySelector('.inbox-container');
    let messages = messageContainer.querySelectorAll('.message');
    messages.forEach(function(message) {
        let subjectType = message.getAttribute('type');
        if (filter === 'all' || filter === subjectType) {
            message.style.display = '';
        }
        else {
            message.style.display = 'none';
        }
    });
}

function createBlock(msg, type, isNewMsg = true) {
    let li_message = document.createElement("li");
    li_message.classList.add("message");
    if (isNewMsg) li_message.classList.add("unread");

    let div_messageHeader = document.createElement("div")
    div_messageHeader.classList.add("message-header")
    let span_statusDot = document.createElement("span")
    let span_sender = document.createElement("span")
    let span_subject = document.createElement("span")

    let TYPES = {
        'FR': 'Follow Request',
        'LK': 'Like',
        'CM': 'Comment',
        'NP': 'New Post Reminder',
        'SU': 'New Sign Up'
    }

    span_statusDot.classList.add("status-dot")
    span_subject.classList.add("subject")
    span_subject.textContent = `[New] ${TYPES[type]} `;
    span_sender.classList.add("sender")
    span_sender.textContent = "from " + msg.origin + " ";
    div_messageHeader.appendChild(span_statusDot)
    div_messageHeader.appendChild(span_subject)
    div_messageHeader.appendChild(span_sender)

    let div_messageBody = document.createElement("div")
    div_messageBody.classList.add("message-body")
    let p_text = document.createElement("p")
    p_text.textContent = msg.content;
    p_text.classList.add("message-text")
    let button_delete = document.createElement("button")
    button_delete.classList.add("inbox-delete-btn")
    button_delete.textContent = "Delete"
    button_delete.setAttribute('ID', msg.id);
    let button_star = document.createElement("button")
    button_star.classList.add("inbox-star-btn")
    button_star.textContent = "Star"

    div_messageBody.appendChild(p_text)
    div_messageBody.appendChild(button_delete)
    div_messageBody.appendChild(button_star)
    li_message.appendChild(div_messageHeader)
    li_message.appendChild(div_messageBody)
    li_message.setAttribute('type', type);
    return li_message
}


async function loadAndDisplayMessages() {
    let messageTypes = ['FR', 'LK', 'CM', 'NP', 'SU']; // Array of message types
    let ul_inboxMsgContainer = document.getElementById('msgContainer');
    ul_inboxMsgContainer.innerHTML = '';

    for (let type of messageTypes) {
        try {
            let messages = await getMessages(type);
            if (messages && Array.isArray(messages)) {
                for (let msg of messages) {
                    let li_message = createBlock(msg, type);
                    ul_inboxMsgContainer.appendChild(li_message);
                }
            }
            else {
                console.error(`Messages of type [${type}] are not an array.`);
            }
        } catch (error) {
            console.error(`An error occurred while fetching messages of type ${type}:`, error);
        }
    }
}


function deleteMessage() {
    const deleteButtons = document.getElementsByClassName('inbox-delete-btn');

    for (let button of deleteButtons) {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            let messageID = event.target.getAttribute("ID");
            let isDeleted = deleteMessageID(parseInt(messageID));
            if (isDeleted) {
                alert("Message Deleted")
                location.reload();
            }
            else {
                alert("Fail to Delete Message")
            }
        })
    }

    let filterForm = document.getElementById('filter-form');
    filterForm.addEventListener('reset', function(event) {
        event.preventDefault();
        let type = document.getElementById('filter').value;
        if (type === 'all') {
            alert("Warning: You Are Deleting All Messages!! (Re-click To Confirm)")
            filterForm.addEventListener('reset', function(event) {
                event.preventDefault();
                for (let type of ['FR', 'LK', 'CM', 'NP', 'SU']) {
                    deleteMessageType(type);
                }
                alert(`All Messages Are Deleted`);
                location.reload();
            });
        }
        else {
            let isDeleted = deleteMessageType(type);
            if (isDeleted) {
                alert(`All In-type Messages Are Deleted`);
                location.reload();
            }
            else {
                alert("Fail to Delete Message");
            }
        }
    });
}


document.addEventListener('DOMContentLoaded', async function() {
   /*
    await createMessage("SU", "SU", "Eden1");
    await createMessage("CM", "CM", "Eden2");
    await createMessage("LK", "LK", "Eden3");
    await createMessage("FR", "FR", "Eden4");
*/
    await loadAndDisplayMessages();
    clickableFilterMessages();
    clickableListItem(document.querySelectorAll('.inbox-messages .message'));
    deleteMessage()
});
