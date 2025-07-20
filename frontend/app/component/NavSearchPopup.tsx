"use client";
import React, { useEffect, useState } from "react";
import CATEGORIES from "../categories";
import { toast } from 'react-toastify';

function NavSearchPopup() {
    const [selected, setSelected] = useState({ key: "all", label: "All" });
    const [searchText, setSearchText] = useState("");
    const [screenMode, setscreenMode] = useState("lg");
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
    const handleSearch = () => {
        // search in a category without text
        if (searchText.trim() === "" && selected.key !== "all") {
            document.location.href = "/category/" + selected.key + "?page=1";
        // search in a category with text
        } else if (searchText.trim() !== "" && selected) {
            document.location.href = `/search/${selected.key ? selected.key : "all"}/${searchText}?page=1`;
        } else {
            toast.warning("Please select a category or enter a search term");
        }
    };

    return (
        <div className="offcanvas offcanvas-top h-50 w-100 border-0" id="SearchMenu">
            {/* Header with user icon */}
            <div className="offcanvas-header d-flex align-items-center w-100 border-bottom justify-content-between">
                {/* Brand Logo */}
                {(screenMode ==="lg" || screenMode == "md") && (
                <a
                href="https://www.kologram.com"
                className="btn btn-link text-contrast d-flex align-items-center"
                aria-label="Kologram Home Page"
                data-testid="link"
                style={{ textDecoration: "none", height: "100%" }}
                >
                    <svg
                        aria-hidden="true"
                        focusable="false"
                        viewBox="0 0 24 24"
                        role="img"
                        width="80px"
                        height="80px"
                        fill="none"
                    >
                        <path
                        fill="currentColor"
                        d="M4 13c1.5 3 4.5 4.5 8 4.5s6.5-1.5 8-4.5c.2-.4.2-.8-.1-1.1-.3-.3-.8-.3-1.1 0-1.2 2.5-3.7 3.6-6.8 3.6s-5.6-1.1-6.8-3.6c-.2-.4-.7-.5-1.1-.2-.3.3-.4.7-.1 1.1z"
                        />
                    </svg>
                </a>
                )}

                {/* Search Bar */}
                <div className="d-flex position-relative mx-auto " style={{ width: "100%" }}>
                    <div className="dropdown">
                        <button
                            className="btn dropdown-toggle border rounded-start-5 d-flex align-items-center justify-content-between h-100"
                            type="button"
                            data-bs-toggle="dropdown"
                            aria-expanded="false"
                            style={{ 
                            maxWidth: "160px", 
                            minWidth: "120px", 
                            whiteSpace: "nowrap", 
                            overflow: "hidden", 
                            paddingRight: "2rem",
                            position: "relative"
                            }}
                            title={selected ? selected.label : "Select Category"}
                        >
                            <span 
                            className="text-truncate" 
                            style={{ display: "inline-block", maxWidth: "100%", paddingRight: "1rem" }}
                            >
                            {selected ? selected.label : "Category"}
                            </span>
                        </button>

                        <ul className="dropdown-menu" style={{ maxHeight: '500px', overflowY: 'auto' }}>
                            {CATEGORIES.map(([key, label]) => (
                            <li key={key}>
                                <button
                                className="dropdown-item text-truncate"
                                type="button"
                                title={label}
                                onClick={() => setSelected({ key, label })}
                                >
                                {label}
                                </button>
                            </li>
                            ))}
                        </ul>
                    </div>

                    <input
                        className="form-control fs-5 pe-5 rounded-pill rounded-start-0"
                        type="search"
                        placeholder="Search"
                        aria-label="Search"
                        name="search"
                        id="search"
                        style={{ minWidth: "0"}}
                        value={searchText}
                        onChange={(e) => setSearchText(e.target.value)}
                        onSubmit={handleSearch}
                    />

                    <button
                        type="submit"
                        className="btn position-absolute top-50 translate-middle-y border-contrast me-1"
                        style={{
                        right: "10px",
                        background: "transparent",
                        border: "none",
                        padding: "0",
                        }}
                        aria-label="Search"
                        onClick={handleSearch}
                    >
                        <i className="fa fa-search fa-lg" aria-hidden="true" />
                    </button>
                </div>


                {/* Close Button */}
                <button
                type="button"
                className="btn-close"
                data-bs-dismiss="offcanvas"
                aria-label="Close"
                />

            </div>

            {/* Body */}
            {/* Body */}
            <div className="offcanvas-body p-3">
                <div className="row row-cols-2 row-cols-md-3 row-cols-lg-4 g-3">
                    {CATEGORIES.map(([key, label]) => (
                        <div key={key} className="col">
                            <a
                            href={`/category/${key}`}
                            className="btn text-contrast w-100 text-start rounded-4 p-3 shadow-sm"
                            >
                            {label}
                            </a>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

export default NavSearchPopup;
