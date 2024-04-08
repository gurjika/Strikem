

const img = document.getElementById('largeImage');
const containerDiv = document.querySelector('.div-container');


document.addEventListener("DOMContentLoaded", () => {
    document.getElementById('north').addEventListener('click', () => { navigate('north'); });
    document.getElementById('west').addEventListener('click', () => { navigate('west'); });
    document.getElementById('east').addEventListener('click', () => { navigate('east'); });
    document.getElementById('south').addEventListener('click', () => { navigate('south'); });

    


    function handleResize() {
        navigate('', true);

        
        const imgContainer = document.getElementById('imageContainer');

        



        containerDiv.style.height = `${imgContainer.offsetHeight * 2}px`;
        containerDiv.style.width = `${imgContainer.offsetWidth * 3}px`;


       
      

    }



    window.addEventListener('resize', handleResize);



    handleResize();
});



function navigate(direction, resizing) {

    const img = document.getElementById('largeImage');
    const imgContainer = document.getElementById('imageContainer');


    const stepVertical = img.offsetHeight / 2;
    const stepHorizontal = imgContainer.offsetWidth;

    

    img.style.width = `${imgContainer.offsetWidth * 3}px`;
    imgContainer.style.height = `${img.offsetHeight / 2}px`;



    let imageTop = parseInt(img.style.top, 10);
    let imageLeft = parseInt(img.style.left, 10);


    let containerTop = parseInt(containerDiv.style.top, 10);
    let containerLeft = parseInt(containerDiv.style.left, 10);



    

    if (resizing) {
        img.style.top = `0px`;
        img.style.left = `0px`;
        containerDiv.style.top = `0px`;
        containerDiv.style.left = `0px`;
    }


    else {

        switch(direction) {
        case 'north':
        img.style.top = `${imageTop + stepVertical}px`;
        containerDiv.style.top = `${containerTop + stepVertical}px`;
        break;
        case 'south':
        img.style.top = `${imageTop - stepVertical}px`;
        containerDiv.style.top = `${containerTop - stepVertical}px`;

        break;
        case 'west':
        img.style.left = `${imageLeft + stepHorizontal}px`;
        containerDiv.style.left = `${containerLeft + stepHorizontal}px`;

        break;
        case 'east':
        img.style.left = `${imageLeft - stepHorizontal}px`;
        containerDiv.style.left = `${containerLeft - stepHorizontal}px`;

        break;
    }

    }
    
}
