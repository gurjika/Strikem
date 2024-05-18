function makeMeActive(location) {
    const navlinks = document.querySelectorAll('.nav-link');
    navlinks.forEach(navlink => {
      navlink.classList.remove('active');
      navlink.classList.remove('active-nav-link');
      navlink.style.textDecoration = 'none';

      if(navlink.id === location) {
        navlink.classList.add('active');
        navlink.style.textDecoration = 'underline';
      }
    });
  }