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
    var toastLiveExample = document.getElementById('liveToast');
    var toast = new bootstrap.Toast(toastLiveExample);
    const joinedUsername = data.username;
    var invitationHeader = document.querySelector('#toast-header-text .me-auto').innerText = 'User State';
    if(data.protocol === 'handleUserState' && data.username !== username){ 
        if (data.user_state === 'joined') {
            const toastBody = document.querySelector('.toast-body').innerText = `${data.username} joined`;
        }
        else {
            const toastBody = document.querySelector('.toast-body').innerText = `${data.username} left`;

    
        }

        toast.show();


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



