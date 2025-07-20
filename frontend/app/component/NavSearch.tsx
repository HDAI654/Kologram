"use client";
import React, { useEffect, useState } from "react";
import { toast } from 'react-toastify';
import NavSearchPopup from "./NavSearchPopup";

function NavSearch() {
    const [screenMode, setscreenMode] = useState("lt");

    useEffect(() => {
        handleResize();
        window.addEventListener("resize", handleResize)
    }, []);

    const handleResize = () => {
    let width = window.innerWidth
        if (width < 400) {
        setscreenMode("lt");
        return;
        }else if (width < 600) {
        setscreenMode("sm");
        return;
        }else if (width < 1000) {
        setscreenMode("md");
        return;
        }else {
        setscreenMode("lg");
        return;
        }
    };

    return (
        <>
            {/* Search */}
            <div className="position-relative scale-in" style={{ maxWidth: "500px", minWidth: "0px" }}>
                {screenMode==="lg" && (
                <input
                    className="form-control pe-5 rounded-pill fade-in-up"
                    type="search"
                    placeholder="Search"
                    aria-label="Search"
                    name="search"
                    id="search"
                    data-bs-toggle="offcanvas"
                    data-bs-target="#SearchMenu"
                />
                )} 

                <button
                    type="submit"
                    className="btn position-absolute top-50 translate-middle-y border-contrast"
                    style={{
                    right: "10px",
                    background: "transparent",
                    border: "none",
                    padding: "0",
                    }}
                    aria-label="Search"
                    data-bs-toggle="offcanvas" 
                    data-bs-target="#SearchMenu"
                >
                    <i className={`fa fa-search fa-lg ${screenMode==="lg" ? null : "text-body"}`} aria-hidden="true" />
                </button>
            </div>


            {/* Search Popup */}
            <NavSearchPopup />

        </>
    );
}

export default NavSearch;
