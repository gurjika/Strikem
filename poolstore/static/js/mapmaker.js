const sectionNumHorizontal = 3;
const sectionNumVertical = 4;


let positionVertical = 1;
let positionHorizontal = 1;

const img = document.getElementById('largeImage');
const overlayDiv = document.querySelector('.div-container');
const imgContainer = document.getElementById('imageContainer');

document.addEventListener("DOMContentLoaded", () => {
    
    document.getElementById('north').addEventListener('click', () => { navigate('north'); });
    document.getElementById('west').addEventListener('click', () => { navigate('west'); });
    document.getElementById('east').addEventListener('click', () => { navigate('east'); });
    document.getElementById('south').addEventListener('click', () => { navigate('south'); });

    function handleResize() {
        document.body.style.overflow = 'hidden';

        const containerWidth = imgContainer.getBoundingClientRect().width;
    
        // Reset scrollbar
        document.body.style.overflow = '';

        overlayDiv.style.width = `${containerWidth * sectionNumHorizontal}px`;
        const rect = img.getBoundingClientRect();
    
        overlayDiv.style.height = `${rect.height}px`;
        imgContainer.style.height = `${img.getBoundingClientRect().height / sectionNumVertical}px`;
    
    
        
        navigate('', true);

    }


    if (img.complete) {
        handleResize();
    } else {
        img.onload = handleResize;
    }
    
    window.addEventListener('resize', handleResize);
});



function navigate(direction, resizing) {
    
    
    
    if (resizing) {
        
        overlayDiv.style.top = `0px`;
        overlayDiv.style.left = `0px`;
        positionHorizontal = 1;
        positionVertical = 1;
    }
    
    
    else {
        const stepVertical = Number((img.getBoundingClientRect().height / sectionNumVertical).toFixed(2));
        const stepHorizontal = Number((img.getBoundingClientRect().width / sectionNumHorizontal).toFixed(2));

        let overlayTop = parseInt(overlayDiv.style.top, 10);
        let overlayLeft = parseInt(overlayDiv.style.left, 10);


        let topSign, leftSign;
        let exact;

        topSign = Math.sign(overlayTop);
        topSign = (topSign === 0) ? -1 : topSign
        

        leftSign = Math.sign(overlayLeft);
        leftSign = (leftSign === 0) ? -1 : leftSign




        
        switch(direction) {
        case 'north':

        positionVertical -= 1;
        exact = stepVertical * (positionVertical - 1) * topSign;
        overlayDiv.style.top = `${exact}px`;
        break;

        case 'south':
        positionVertical += 1;
        exact = stepVertical * (positionVertical - 1) * topSign;
        overlayDiv.style.top = `${exact}px`;

        break;


        case 'west':
        positionHorizontal -= 1;
        exact = stepHorizontal * (positionHorizontal - 1) * leftSign;
        overlayDiv.style.left = `${exact}px`;
        break;
        

        case 'east':
        positionHorizontal += 1;
        exact = stepHorizontal * (positionHorizontal - 1) * leftSign;
        overlayDiv.style.left = `${exact}px`;
        console.log()
        break;
    }

    }

    checkNextDirection();
    
}

function checkDirection(buttonId, position, maxSections) {
    if (position === 0 || position === maxSections + 1) {
        disableButton(buttonId);
    } else {
        enableButton(buttonId);
    }
}

function checkNextDirection() {
    checkDirection('east', positionHorizontal + 1, sectionNumHorizontal);
    checkDirection('west', positionHorizontal - 1, sectionNumHorizontal);
    checkDirection('south', positionVertical + 1, sectionNumVertical);
    checkDirection('north', positionVertical - 1, sectionNumVertical);
}


function disableButton(direction) {
    var button = document.getElementById(direction);
    button.disabled = true; 
}

function enableButton(direction) {
    var button = document.getElementById(direction);
    button.disabled = false;
}

