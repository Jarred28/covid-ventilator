function toggleSubmenu () {
  $(this).find('> .dropdown-menu').toggle();
  $(this).find('> a.dropdown-toggle').click(function (e) {
    e.stopPropagation();
    e.preventDefault();
  });
}

$('.drop-submenu').hover(toggleSubmenu, toggleSubmenu);
