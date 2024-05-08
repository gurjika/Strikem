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

    else if (data.protocol === 'handleMessage'){

        
         var sentByElements = document.querySelectorAll('.sent-by');
            if (sentByElements.length > 0) {
                var lastSentBy = sentByElements[sentByElements.length - 1]; 

                if (lastSentBy.innerText === data.username) {
                    lastSentBy.parentNode.removeChild(lastSentBy); 
                }
            }
      
     
            
        
         
        let messageHtml = ``;

        if(data.sub_protocol === 'last_message_outdated') {
            console.log('herr');
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
                    <div>
                        <div class="bg-primary rounded text-white px-3 py-2">
                            ${data.message}
                        </div>

                        <div class="text-secondary text-end sent-by">
                            ${data.username}
                        <div>
                    
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
            
    
                    <div>
                        <div class="bg-light rounded text-secondary px-3 py-2">
                            ${data.message}
                        </div>

                        <div class="text-secondary text-start sent-by">
                            ${data.username}

                        <div>
                
                    </div>
                </div>
            </div>
          `
             ;

        }

      
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




 


