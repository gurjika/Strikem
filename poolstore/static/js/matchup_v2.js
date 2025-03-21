var matchupId = JSON.parse(document.getElementById('matchup_id').textContent);
var username = JSON.parse(document.getElementById('username').textContent);
var opponentUsername = JSON.parse(document.getElementById('opponent_username').textContent);

import socket from "./websocket";



var matchUpSocket = new WebSocket(
    'wss://' + 
    window.location.hostname + 
    '/ws/base/' + 
    username + 
    '/'
);


// socket.onopen = function (e) {
//     socket.send(JSON.stringify({
//         'username': username,
//         'user_state': 'joined',
//         'opponent_username': opponentUsername,
//     }));
// }





socket.onmessage = function (e) {

    const data = JSON.parse(e.data);

    // if(data.protocol === 'handleUserState' && data.username !== username){ 
    //     var toastLiveExample = document.getElementById('liveToast');
    //     var toast = new bootstrap.Toast(toastLiveExample);
    //     var invitationHeader = document.querySelector('#toast-header-text .me-auto').innerText = 'User State';
    //     if (data.user_state === 'joined') {

    //         const toastBody = document.querySelector('.toast-body').innerText = `${data.username} joined`;
    //         console.log(data.username);
    //         changeStatusOn(data);


    //         socket.send(JSON.stringify(
    //             {
    //                 'protocol': 'acknowledge',
    //                 'active_user': data.username,
    //             }
    //         ))

    //     }
    //     else {
    //         const toastBody = document.querySelector('.toast-body').innerText = `${data.username} left`;
    //         changeStatusOff(data);
    
    //     }

    //     toast.show();

    // }

    // else if(data.protocol === 'handleAcknowledge'){
    //     changeStatusOn(data);

    // }

    if (data.protocol === 'handleMessage'){
        const messageReceivedEvent = new CustomEvent('messageReceived', {
        });
        
        const matchupHold = document.getElementById('matchup-hold');

        matchupHold.dispatchEvent(messageReceivedEvent);


        document.addEventListener('messageReceived', (e) => {
        });
        
         var sentByElements = document.querySelectorAll('.sent-by');
            if (sentByElements.length > 0) {
                var lastSentBy = sentByElements[sentByElements.length - 1]; 

                if (lastSentBy.innerText === data.username) {
                    lastSentBy.parentNode.removeChild(lastSentBy); 
                }
            }
      
     
            
        
         
        let messageHtml = ``;

        if(data.sub_protocol === 'last_message_outdated') {
            console.log(data.time_sent);
            messageHtml += `
            <div class="d-flex justify-content-center text-center my-3">
                <div>   
                    ${data.time_sent}
                </div>
            </div>
            `;
        }

        if(data.username === username) {

           

            messageHtml += `
            <div class="d-flex justify-content-end text-center my-3">
                <div class="w-75 d-flex justify-content-end">
                    <div class="d-flex flex-column">

                        <div class="d-flex justify-content-end">
                            <div class="bg-primary rounded text-white px-3 py-2 text-start">
                                ${data.message}
                            </div>
                        </div>
            
                        <div class="d-flex justify-content-end">
                            <div class="text-secondary text-end sent-by">
                                ${data.username}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            `
             ;

        }
        else {
            messageHtml += `
            <div class="d-flex justify-content-start text-center my-3">
                <div class="w-75  d-flex justify-content-start">
                
                    <div class="d-flex flex-column">

                       <div class="d-flex justify-content-start">
                           <div class="bg-light rounded text-secondary px-3 py-2 text-start">
                               ${data.message}
                           </div>
                       </div>
           
                       <div class="d-flex justify-content-start">
                           <div class="text-secondary text-start sent-by">
                               ${data.username}
                           </div>
                       </div>
                   </div>
    
                </div>
            </div>
          `
             ;

        }

      
        const newMessageHold = document.querySelector('.new-message');
        console.log(data.matchup_id);
        if( newMessageHold.id === data.matchup_id ) {
            newMessageHold.innerHTML += messageHtml;
        }

        scrollBottom();
    }

};



function scrollBottom() {
    var objDiv = document.getElementById("message-hold");
    objDiv.scrollTop = objDiv.scrollHeight;
 }





function readySendMessage() {
    document.querySelector('#submit').onclick = function (e) {

        const messageInputDom = document.querySelector('#input');
        const message = messageInputDom.value;
        console.log(username);
        console.log(opponentUsername)




        socket.send(JSON.stringify({
            'action': 'matchup',    
           'message': message,
           'username': username,
           'opponent_username': opponentUsername,
           'matchup_id': matchupId,
        }));




        messageInputDom.value = '';
     }
}


function showActiveMessageHeader() {
    
    var messageHeaders = document.querySelectorAll('.message-header');

    messageHeaders.forEach(function(messageHeader) {
        
        messageHeader.classList.remove('active')

        if(messageHeader.id === matchupId) {
            messageHeader.classList.add('active');
        }


    messageHeader.addEventListener('click', function() {

        messageHeaders.forEach(function(messageHeader) {

            messageHeader.classList.remove('active');
        });
        this.classList.add('active');
    });
    });
}





function changeStatusOn(data) {
    var statuses = document.querySelectorAll(`.show-status`);

    statuses.forEach(function(status) {
   
        if(status.id === data.username) {
            status.classList.remove('bg-danger');
            status.classList.add('bg-success');
        }
    });
}


function changeStatusOff(data) {
    var statuses = document.querySelectorAll(`.show-status`);
    statuses.forEach(function(status) {
   
        if(status.id === data.username) {
            status.classList.add('bg-danger');
            status.classList.remove('bg-success');
        }
    });
}



function changeMessageOrder() {
    
}