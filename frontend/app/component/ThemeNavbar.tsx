'use client';

import React, { useState, useEffect } from "react";
import { toast } from 'react-toastify';
import '@/public/entry-styles.css';

function ThemeToggleButton({ screenMode }: { screenMode: string }) {
  const [theme, setTheme] = useState<"light" | "dark">("dark");

  const handleThemeChange = () => {
    try {
      const newTheme = theme === "light" ? "dark" : "light";
      setTheme(newTheme);
      document.documentElement.setAttribute("data-bs-theme", newTheme);
    } catch (error) {
      toast.error("Error in toggle theme");
    }
  };

  return (
    <button
      onClick={handleThemeChange}
      aria-label={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
      type="button"
      className={`btn btn-${theme === "light" ? "dark" : "light"} scale-in`}
      style={{
        position: "fixed",
        bottom: "20px",
        right: "20px",
        zIndex: 1050,
        borderRadius: "50%",
        width: "50px",
        height: "50px",
        padding: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
        marginBottom: screenMode !== "lg" ? "90px" : "0",
      }}
      title={`Switch to ${theme === "light" ? "dark" : "light"} mode`}
    >
      {theme === "light" ? "🌙" : "☀️"}
    </button>
  );
}

export default ThemeToggleButton;
