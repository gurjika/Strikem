const username = JSON.parse(document.getElementById('username').textContent);
const matchSocket = new WebSocket(
    'ws://' + 
    window.location.host + 
    '/ws/matchmake/'
);


        
document.getElementById('control-btn').onclick = function (e) {
    console.log(username);
    matchSocket.send(JSON.stringify(
        {
            'username': username,
        }
    ));
    
    const controlButton = document.getElementById('control-btn');
    let newControl = '';

    if (controlButton.innerText === 'ADD MYSELF') {
        newControl = 'REMOVE MYSELF';
    }

    else {
        newControl = 'ADD MYSELF';
    }

    controlButton.innerText = newControl;
};

document.getElementById('matches-container').addEventListener('click', function(e) {

    if (e.target && e.target.classList.contains('invite-btn')) {
        const matchMakerUsername = e.target.dataset.inviteeUserUsername;
        matchSocket.send(JSON.stringify({
            'matchmaker_username': matchMakerUsername,
            'username': username,
        }));
    }
});


matchSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    
    if (data.protocol === 'add'){
        const html = ` 
        <div id="matches" data-user-username=${data.username}>

            <div>
                ${data.username}
            </div>

            <div>
                <button class='invite-btn' data-invitee-user-username="${data.username}">
                    INVITE
                </button>
            </div>
        </div>`

        document.getElementById('matches-container').innerHTML += html;
    }
    else if (data.protocol === 'delete') {
        var element = document.querySelector(`[data-user-username="${data.username}"]`);

        if (element) {
            element.remove();
        }
    }


    else if (data.protocol === 'invited') {

        const html = `<div>${data.inviteSenderUsername} Sent you an invitation </div>`;
        console.log(html);
        document.querySelector('.invite-notification-container').innerHTML += html;
    }
};
