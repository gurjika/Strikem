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
    
    if (data.user_state === 'joined') {
        document.querySelector('.username-test-holder').innerHTML += joinedUsername + ' joined' + '\n';
    }
    else {
        document.querySelector('.username-test-holder').innerHTML += joinedUsername + ' left' + '\n';

    }


};


