// animation au scroll
(function() {
    function initReveal() {
        var elements = document.querySelectorAll('[data-reveal]');
        // tous les elems avec l'attribut data-reveal
        if (!elements.length) return; // si on trouve pas on s'arrete

        // IntersectionObserver c'est un outil du navigateur qui
        // surveille si un élément entre dans la zone visible de l'écran
        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        var delay = entry.target.getAttribute('data-reveal-delay') || 0;
                        setTimeout(function() {
                            entry.target.classList.add('is-revealed'); // apres le delai on ajoute cette classe pour declancher l'animation
                        }, parseInt(delay));
                        observer.unobserve(entry.target); // arrete de surveiller pour pas refaire l'animation
                    }
                });
            }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

            elements.forEach(function(el) { observer.observe(el); });
        } else {
            elements.forEach(function(el) { el.classList.add('is-revealed'); });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initReveal);
    } else {
        initReveal();
    }
})();

function initDarkMode() {
    //verifier si le dark mode est deja active
    var isDark = localStorage.getItem('medicss_dark') === 'true';
    if (isDark) {
        // l'appliquer directement sans cliquer la dessus encore une autre fois
        document.body.classList.add('dark-mode');
        document.documentElement.classList.add('dark-mode');
    }

    // Creer le bouton
    var btn = document.createElement('button');
    btn.id = 'dark-mode-toggle';
    btn.className = 'dark-toggle-navbar';
    btn.innerHTML = isDark
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:20px;height:20px;"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:20px;height:20px;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    btn.type = 'button';

    // l'inserer dans la navbar
    var navbar = document.querySelector('#top_menu') ||
                 document.querySelector('.navbar-nav') ||
                 document.querySelector('nav .container');

    if (navbar) {
        var li = document.createElement('li');
        li.className = 'nav-item d-flex align-items-center';
        li.appendChild(btn);
        navbar.appendChild(li);
    } else {
        document.body.appendChild(btn);
    }
    // au click isDark deviendra !isDark, on inverse apres on sauvgarde
    btn.addEventListener('click', function() {
        isDark = !isDark;
        document.body.classList.toggle('dark-mode', isDark);
        document.documentElement.classList.toggle('dark-mode', isDark);
        localStorage.setItem('medicss_dark', isDark);
        btn.innerHTML = isDark
    ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:20px;height:20px;"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>'
    : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:20px;height:20px;"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
    }); // changer l'icone
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDarkMode);
} else {
    initDarkMode();
}