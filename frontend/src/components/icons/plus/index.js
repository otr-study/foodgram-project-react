import * as React from "react";
import { ThemeContext } from '../../../contexts';
import { useContext } from 'react'

const PlusIcon = (props) => {
  const themeContext = useContext(ThemeContext);

  return (
    <svg
      width={16}
      height={17}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path
        d="M8 1.5v14M1 8.5h14"
        stroke={themeContext === 'light' ? props.fill || '#fff' : '#8fb6e4'}
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default PlusIcon