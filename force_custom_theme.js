// Force custom theme and hide settings menu
(function() {
    // Hide settings menu completely
    function hideSettingsMenu() {
        const settingsButton = document.querySelector('[data-testid="stToolbar"]');
        const mainMenu = document.querySelector('#MainMenu');
        const header = document.querySelector('header');
        const footer = document.querySelector('footer');
        
        if (settingsButton) settingsButton.style.display = 'none';
        if (mainMenu) mainMenu.style.visibility = 'hidden';
        if (header) header.style.visibility = 'hidden';
        if (footer) footer.style.visibility = 'hidden';
    }
    
    // Force custom theme by overriding system preferences
    function forceCustomTheme() {
        // Override CSS custom properties for theme
        document.documentElement.style.setProperty('--primary-color', '#4CAF50');
        document.documentElement.style.setProperty('--background-color', 'transparent');
        document.documentElement.style.setProperty('--secondary-background-color', 'rgba(255, 255, 255, 0.1)');
        document.documentElement.style.setProperty('--text-color', '#FFFFFF');
        
        // Add custom theme class to body
        document.body.classList.add('custom-theme-forced');
        document.body.classList.remove('light-theme', 'dark-theme');
    }
    
    // Run immediately
    hideSettingsMenu();
    forceCustomTheme();
    
    // Run again after DOM changes (Streamlit re-renders)
    const observer = new MutationObserver(function(mutations) {
        hideSettingsMenu();
        forceCustomTheme();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    // Also run on window load
    window.addEventListener('load', function() {
        hideSettingsMenu();
        forceCustomTheme();
    });
})();