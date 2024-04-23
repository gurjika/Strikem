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
    }));
}



matchUpSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    const username = data.username;
    document.querySelector('.username-test-holder').innerHTML += username + '\n';


};
