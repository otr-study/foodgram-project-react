import { useEffect, useState } from "react";

const handleThemeSwitch = () => {
    const currentTheme = getCurrentTheme() === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    localStorage.setItem('theme', currentTheme);
}

const getCurrentTheme = () => {
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        return currentTheme;
    }
    return 'light';
}

const useThemeState = (value) => {
    const [themeState, setThemeState] = useState(value);

    return [
        themeState,
        (value) => {
            document.documentElement.setAttribute('data-theme', value);
            localStorage.setItem('theme', value);
            setThemeState(value);
        }
    ]
}

export { getCurrentTheme, useThemeState };