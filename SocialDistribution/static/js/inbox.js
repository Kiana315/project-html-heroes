'use strict';

import {
    getMessages,
    createMessage,
    deleteMessage,
} from './messageOperations.js';


function clickableListItem() {
    document.addEventListener('DOMContentLoaded', function() {
        let messages = document.querySelectorAll('.inbox-messages .message');
        messages.forEach(function(message) {
            message.querySelector('.message-header').addEventListener('click', function() {
                message.classList.toggle('unfolded');
            });
        });
    });
}


function clickableFilterMessages() {
    document.addEventListener('DOMContentLoaded', function() {
        let filterForm = document.getElementById('filter-form');
        filterForm.addEventListener('submit', function(event) {
            event.preventDefault();
            let filterValue = document.getElementById('filter').value;
            filterAndDisplayMessages(filterValue);
        });
    });
}

function filterAndDisplayMessages(filter) {
    let messageContainer = document.querySelector('.inbox-container');
    let messages = messageContainer.querySelectorAll('.message');

    messages.forEach(function(message) {
        let subjectType = message.getAttribute('type');
        if (filter === 'all' || filter === subjectType) {
            message.style.display = '';
        } else {
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

    span_statusDot.classList.add("status-dot")
    span_sender.classList.add("sender")
    span_sender.textContent = msg.sender;
    span_subject.classList.add("subject")
    span_subject.textContent = type;
    div_messageHeader.appendChild(span_statusDot)
    div_messageHeader.appendChild(span_sender)
    div_messageHeader.appendChild(span_subject)

    let div_messageBody = document.createElement("div")
    div_messageBody.classList.add("message-body")
    let p_text = document.createElement("p")
    p_text.textContent = msg.text;
    p_text.classList.add("message-text")
    let button_delete = document.createElement("button")
    button_delete.classList.add("inbox-delete-btn")
    button_delete.textContent = "Delete"
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



/* TESTS */
createMessage("FR", "aaa");
createMessage("LK", "bbb");
createMessage("NP", "ccc");


clickableListItem();
clickableFilterMessages();

let ul_inboxMsgContainer = document.getElementById("inbox-messages-container");
for (let type in ['FR', 'LK', 'CM', 'NP', 'SU']) {
    for (let message in getMessages(type)) {
        let li_message = createBlock(message, type);
        ul_inboxMsgContainer.appendChild(li_message);
    }
}
