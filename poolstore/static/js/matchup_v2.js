const matchupId = JSON.parse(document.getElementById('matchup_id').textContent);
const username = JSON.parse(document.getElementById('username').textContent);


const matchUpSocket = new WebSocket(
    'ws://' + 
    window.location.host + 
    '/ws/matchup/'
    + matchupId 
    + '/'
);

matchUpSocket.onopen = function (e) {
    matchUpSocket.send(JSON.stringify({
        'username': username,
        'user_state': 'joined'
    }));
}



matchUpSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const joinedUsername = data.username;
    if(data.protocol === 'handleUserState'){
        if (data.user_state === 'joined') {
            document.querySelector('.username-test-holder').innerHTML += joinedUsername + ' joined' + '\n';
        }
        else {
            document.querySelector('.username-test-holder').innerHTML += joinedUsername + ' left' + '\n';
    
        }
    }

    else {

        const messageHtml = `${data.message} <hr>`;
        document.getElementById('new-message').innerHTML += messageHtml;
        scrollBottom();

    }
 


};









document.querySelector('#submit').onclick = function (e) {
    const messageInputDom = document.querySelector('#input');
    const message = messageInputDom.value;
    matchUpSocket.send(JSON.stringify({
        'message': message,
        'username': username
    }));
    messageInputDom.value = '';
}


function scrollBottom() {
    var objDiv = document.getElementById("message-hold");
    objDiv.scrollTop = objDiv.scrollHeight;
 }

 scrollBottom();



