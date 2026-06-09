// Function to set the theme and save it to the browser's local storage
function setTheme(themeName) {
    document.documentElement.setAttribute('data-theme', themeName);
    localStorage.setItem('erp_theme', themeName);
}

// Check if the user already chose a theme in a previous visit
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('erp_theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    }
});