const username = JSON.parse(document.getElementById('username').textContent);
        console.log(username);
        const matchSocket = new WebSocket(
            'ws://' + 
            window.location.host + 
            '/ws/matchmake/'
        );


        
document.getElementById('add').onclick = function (e) {
    matchSocket.send(JSON.stringify(
        {
            'username': username
        }
    ));
    
    const controlButton = document.getElementById('add');
    let newControl = '';
    if (controlButton.innerText === 'ADD MYSELF') {
        newControl = 'REMOVE MYSELF';
    }
    else {
        newControl = 'ADD MYSELF';
    }

    controlButton.innerText = newControl;
};


matchSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    if (data.protocol === 'add'){
        const html = ` 
        <div style="display: flex; align-items: center; justify-content: space-between;" id="matches" data-user-username=${username}>
            
            <div>
                ${data.username}
            </div>

            <div>
                <button>
                    INVITE
                </button>
            </div>
        </div>`

        document.getElementById('matches-container').innerHTML += html;
    }
    else {
        var element = document.querySelector(`[data-user-username="${username}"]`);

        if (element) {
            element.remove();
        }
    }


};
