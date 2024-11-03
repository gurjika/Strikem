const poolhouseName = JSON.parse(document.getElementById('poolhouse_name').textContent);

console.log(poolhouseName);
const chatSocket = new WebSocket(
    'wss://' +
    window.location.host +
    '/ws/poolhouses/' +
    poolhouseName + 
    '/'
);


chatSocket.onmessage = function (e) {



    const data = JSON.parse(e.data);
    console.log(data.changed);
    document.getElementById('first-table').innerText = data.changed;

    
};


document.querySelector('#change-button').onclick = function (e) {

    const currentTableState = document.getElementById('first-table').innerText;


    let newTableState = ''

    if (currentTableState === 'reserved')  {
        newTableState = 'free';
    }

    else {
        newTableState = 'reserved';
    }



    chatSocket.send(JSON.stringify({
        'changed': newTableState,
    }));
};