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

    if (controlButton.innerText === 'ADD MYSELF') {
        changeControlButton('remove');

    }
    else {
        changeControlButton('add')
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
        const html =
        `
        <div data-user-username="${data.username}">
            <div class="mt-3 d-flex justify-content-between">
                
                <div class='h4'>
                    ${data.username}
                </div>

                <div>
                    <button class="invite-btn  btn btn-primary" data-invitee-user-username="${data.username}">
                        INVITE
                    </button>
                </div>
            </div>
            <hr>
        </div>

       `;


        document.getElementById('matches-container').innerHTML += html;

        if (data.username === username) {
            var element = document.querySelector(`[data-invitee-user-username="${data.username}"]`);
            element.remove();
        }
    }
    else if (data.protocol === 'delete') {
        var element = document.querySelector(`[data-user-username="${data.username}"]`);

        if (element) {
            element.remove();
        }
    }


    else if (data.protocol === 'invited') {

        var toastLiveExample = document.getElementById('liveToast');
        var toast = new bootstrap.Toast(toastLiveExample);
        const toastBody = document.querySelector('.toast-body').innerText = `${data.inviteSenderUsername} Sent you an invitation`;
        toast.show();
       
        

        const html = `
        <div class='d-flex justify-content-between mt-3'>
            <div class='h5'>
                ${data.inviteSenderUsername} Invited You 
            </div>

            <div class='d-flex'>
                <div style='margin-right: 15px;'>
                    <button class="accept-btn btn btn-success" data-inviter-username=${data.inviteSenderUsername}>
                        ACCEPT
                    </button>
                </div>


                <div>
                    <button class="deny-btn btn btn-danger" data-inviter-username=${data.inviteSenderUsername}>
                        DENY
                    </button>
                </div>
            </div>
         

        </div>`
        
        ;

        // window.location.href = 'http://127.0.0.1:8000/matchup/'

         document.querySelector('.invite-notification-container').innerHTML += html;

       
    }

    else if (data.protocol === 'handling_invite_response'){
        


        if (data.invite_response === 'ACCEPTED') {
            // FOR TESTING
            const url = `http://127.0.0.1:8000/matchup/${data.matchup_id}`
            const htmlMatchup = `
            <div style="width: 200px; height: 200px; display: flex; flex-direction: column;">
                <div>
                    ${data.accepterUsername} vs ${data.inviteSenderUsername}
                </div>
    
                <a href='${url}'>
                    GO TO MATCHUP PAGE  
                </a>
            </div>
        `
        document.querySelector('.matchup-div').innerHTML = htmlMatchup;
        }
        


        if (data.sub_protocol !== 'accepter'){
            const html = `
            <div>
                ${data.accepterUsername} ${data.invite_response} your invitation
            </div>`;

            document.querySelector('.invite-notification-container').innerHTML += html;
        }

    }

    else if (data.protocol === 'accepter_player_cleanup') {
        var elementAccepter = document.querySelector(`[data-user-username="${data.accepter_username}"]`);
        var elementInviter = document.querySelector(`[data-user-username="${data.inviter_username}"]`);

        elementAccepter.remove();
        elementInviter.remove();
        if (username === data.accepter_username || username === data.inviter_username) {
            changeControlButton('add');

        }

    }
};




document.querySelector('.invite-notification-container').addEventListener('click', function(e) {

    if (e.target && e.target.classList.contains('accept-btn')) {
        changeControlButton('add');
        const inviteSender = e.target.dataset.inviterUsername;
        matchSocket.send(JSON.stringify({
            'username': username,
            'invite_sender_username': inviteSender,
            'invite_response': 'accept'
        }));


       

    }

    else if(e.target && e.target.classList.contains('deny-btn')) {
        const inviteSender = e.target.dataset.inviterUsername;
        matchSocket.send(JSON.stringify({
            'username': username,
            'invite_sender_username': inviteSender,
            'invite_response': 'deny'
        }));
    }
});





function changeControlButton(newControl) {
    const controlButton = document.getElementById('control-btn');

    if (newControl === 'add') {
        const invitationContainer = document.querySelector('.invite-notification-container');

        while (invitationContainer.firstChild) {
            invitationContainer.removeChild(invitationContainer.firstChild); 
        }

        controlButton.classList.add('btn-outline-success');
        controlButton.classList.remove('btn-outline-danger');

        controlButton.innerText = 'ADD MYSELF';
    }

    else if (newControl === 'remove') {

        controlButton.classList.remove('btn-outline-success');
        controlButton.classList.add('btn-outline-danger');
        controlButton.innerText = 'REMOVE MYSELF';
    }
}