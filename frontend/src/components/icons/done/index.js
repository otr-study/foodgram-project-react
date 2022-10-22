import * as React from "react";
import { ThemeContext } from '../../../contexts';
import { useContext } from 'react'

function SvgVector2(props) {
  const themeContext = useContext(ThemeContext);
  const color = themeContext === 'light' ? '#4A61DD' : '#8fb6e4';
  return (
    <svg
      width={16}
      height={12}
      fill="transparent"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M1 6l4.667 5L15 1"
        stroke={props.color || color}
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default SvgVector2;