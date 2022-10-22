import { ThemeContext } from '../../../contexts';
import { useContext } from 'react'

const ClockIcon = (props) => {
  const themeContext = useContext(ThemeContext);

  return (
    <svg
      width={20}
      height={20}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M10 18.333a8.333 8.333 0 100-16.666 8.333 8.333 0 000 16.666z"
        stroke={themeContext === 'light' ? "#000" : "#fff"}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M10 5v5l2.5 2.5"
        stroke={themeContext === 'light' ? "#000" : "#fff"}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default ClockIcon
