'use strict';

// theme toggle logic for login page
const themeToggle = document.getElementById('theme-toggle');
const themeToggleText = document.getElementById('theme-toggle-text');
const loginContainer = document.querySelector('.login-container');

function setTheme(dark) {
    if (dark) {
        document.body.classList.add('dark-mode');
        document.documentElement.classList.add('dark-mode');
        if (themeToggleText) themeToggleText.textContent = 'Light Mode';
        if (themeToggle) themeToggle.querySelector('i').className = 'fa-solid fa-sun';
        if (loginContainer) {
            loginContainer.classList.remove('bg-neutral-100', 'text-neutral-900');
            loginContainer.classList.add('bg-neutral-800', 'text-white');
        }

        localStorage.setItem('theme', 'dark');
        
        } else {
        document.body.classList.remove('dark-mode');
        document.documentElement.classList.remove('dark-mode');
        if (themeToggleText) themeToggleText.textContent = 'Dark Mode';
        if (themeToggle) themeToggle.querySelector('i').className = 'fa-solid fa-moon';
        if (loginContainer) {
            loginContainer.classList.remove('bg-neutral-800', 'text-white');
            loginContainer.classList.add('bg-neutral-100', 'text-neutral-900');
        }

        localStorage.setItem('theme', 'light');
    }
}

if (themeToggle) {
    themeToggle.addEventListener('click', () => {
    const isDark = document.body.classList.contains('dark-mode');
    setTheme(!isDark);
    });
}

// on load, set theme from localStorage or system preference
(function() {
    const saved = localStorage.getItem('theme');
    if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        setTheme(true);
    } else {
        setTheme(false);
    }
})();