document.addEventListener('DOMContentLoaded', function() {
    let scrollHeightBefore = 0;
    let scrollTopBefore = 0;
    

})
   function hideSpinner() {
    document.getElementById('spinner').classList.add('invisible');

}

function revealSpinner() {
    document.getElementById('spinner').classList.remove('invisible');
}

if (document.getElementById('sender') !== null) {
    
    document.getElementById('sender').addEventListener('htmx:beforeRequest', function (e) {
        revealSpinner();

        const container = document.getElementById('message-hold');
        scrollTopBefore = container.scrollTop;  
        scrollHeightBefore = container.scrollHeight;
    });

    document.getElementById('sender').addEventListener('htmx:afterSettle', function(e) {
        hideSpinner();
        const container = document.getElementById('message-hold');
        const scrollHeightAfter = container.scrollHeight; 
        container.scrollTop = scrollTopBefore + (scrollHeightAfter - scrollHeightBefore);
    });

}

