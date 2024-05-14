function makeMeActive(location) {
    const navlinks = document.querySelectorAll('.nav-link');
    navlinks.forEach(navlink => {
      navlink.classList.remove('active');
      navlink.classList.remove('link-underline-light');
      ;

      if(navlink.id === location) {
        navlink.classList.add('active');
        navlink.classList.add('link-underline-light');
      }
    });
  }