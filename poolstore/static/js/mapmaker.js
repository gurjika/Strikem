const sectionNumHorizontal = 3;
const sectionNumVertical = 2;

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
    const stepVertical = img.offsetHeight / sectionNumVertical;
    const stepHorizontal = img.offsetWidth / sectionNumHorizontal;

    overlayDiv.style.width = `${imgContainer.offsetWidth * sectionNumHorizontal}px`;
    const rect = img.getBoundingClientRect();
    overlayDiv.style.height = `${rect.height}px`;
    imgContainer.style.height = `${img.offsetHeight / sectionNumVertical}px`;


    let overlayTop = parseInt(overlayDiv.style.top, 10);
    let overlayLeft = parseInt(overlayDiv.style.left, 10);

    if (resizing) {
       
        overlayDiv.style.top = `0px`;
        overlayDiv.style.left = `0px`;
        positionHorizontal = 1;
        positionVertical = 1;
    }


    else {

        switch(direction) {
        case 'north':
        overlayDiv.style.top = `${overlayTop + stepVertical}px`;
        positionVertical -= 1;
        break;

        case 'south':
        overlayDiv.style.top = `${overlayTop - stepVertical}px`;
        positionVertical += 1;

        break;

        case 'west':
        overlayDiv.style.left = `${overlayLeft + stepHorizontal}px`;
        positionHorizontal -= 1;
        break;

        case 'east':
        overlayDiv.style.left = `${overlayLeft - stepHorizontal}px`;
        positionHorizontal += 1;

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

