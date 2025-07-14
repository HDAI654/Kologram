import "bootstrap/dist/css/bootstrap.min.css";
import React, { useState, HTMLAttributes } from "react";

interface NavButtonProps extends HTMLAttributes<HTMLButtonElement> {
  iconName: string;
  text: string;
  buttonOtherClasses: string;
}

function NavButton({ iconName, text, buttonOtherClasses="", ...props }: NavButtonProps) {
  const [showIcon, setShowIcon] = useState(false);

  if (!iconName) return null;

  return (
    <button
      className={`btn btn-success border border-dark ${buttonOtherClasses}`}
      onMouseEnter={() => setShowIcon(true)}
      onMouseLeave={() => setShowIcon(false)}
      {...props}
    >
      <i className={`fas ${iconName} fa-lg`}></i>
      {showIcon && <span>  {text}</span>}
    </button>
  );
}

export default NavButton;
