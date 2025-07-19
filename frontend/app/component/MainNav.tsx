"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React, { useEffect, useState } from "react";
import '@/public/entry-styles.css';
import Sidebar from "./DrawerMenu";
import { toast } from 'react-toastify';
import '@/public/MainNav.css';
import CATEGORIES from "../categories";
import ThemeToggleButton from "./ThemeNavbar";

function MainNavbar() {
    const [screenMode, setscreenMode] = useState("lg");
    const [selected, setSelected] = useState({ key: "all", label: "All" });
    const [isLogin, setIsLogin] = useState(false);
    const [username, setUsername] = useState("Guest");

    const handleSelect = (key:string, label:string) => {
        setSelected({ key, label });
    };

    useEffect(() => {
        import("bootstrap/dist/js/bootstrap.bundle.min.js");
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
        }else if (width < 940) {
        setscreenMode("md");
        return;
        }else {
        setscreenMode("lg");
        return;
        }
    };

    const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault(); // Prevent the default form submission behavior
        const form = e.currentTarget;
        const formData = new FormData(form);
        const text = formData.get("search") || "";

        // search in a category without text
        if (text.trim() === "" && selected.key !== "all") {
            document.location.href = "/category/" + selected.key + "?page=1";
        // search in a category with text
        } else if (text.trim() !== "" && selected) {
            document.location.href = `/search/${selected.key ? selected.key : "all"}/${text}?page=1`;
        } else {
            toast.warning("Please select a category or enter a search term");
        }
    };

    return (
        <>

            {/* Top Navbar */}
            <nav className="navbar border-0 bg-contrast bg-body fixed-top" style={{ height: "var(--navbar-height)"}}>
                <div className="container-fluid d-flex align-items-center w-100">
                    <img src="/NavIcon.svg" className="mx-auto" alt="Brand" style={{ objectFit: "cover", maxWidth: "150px", maxHeight: "80px" }} width="100%" height="100%" />
                    {screenMode !== "sm" && screenMode !== "lt" ? (
                        <br />
                    ): null}

                    {/* Search Bar */}
                    <div className="d-flex flex-grow-1 align-items-center mx-3" style={{ maxWidth: "700px" }}>
                        <form className="d-flex flex-grow-1" onSubmit={handleSearch}>

                            {/* Categories Button */}
                            {screenMode !== "lt" && <>
                                <div className="dropdown">
                                    <button
                                        className="btn btn-success rounded-start-3 rounded-end-0 dropdown-toggle d-flex align-items-center justify-content-between"
                                        type="button"
                                        data-bs-toggle="dropdown"
                                        aria-expanded="false"
                                        style={{ 
                                        maxWidth: "160px", 
                                        minWidth: "120px", 
                                        whiteSpace: "nowrap", 
                                        overflow: "hidden", 
                                        paddingRight: "0.5rem",
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
                                            onClick={() => handleSelect(key, label)}
                                            title={label}
                                            >
                                            {label}
                                            </button>
                                        </li>
                                        ))}
                                    </ul>
                                </div>
                            </>
                            }

                            <input
                                className={`form-control ${screenMode !== "lt" ? "rounded-0 border-end-0" : null}`}
                                style={{ maxWidth: "100%", minWidth: "0" }}
                                type="search"
                                placeholder="Search"
                                aria-label="Search"
                                name="search"
                                id="search"
                            />
                            { screenMode !== "lt" ? (
                                <button className="btn btn-success rounded-end-3 rounded-start-0 me-3" type="submit">
                                    <li className="fa fa-search fa-lg"></li>
                                </button>
                                
                            ) : null}
                        </form>

                        <Sidebar isLogin={isLogin} username={username} screenMode={screenMode} />
                    </div>
                    
                    {/* Login and Cart Button */}
                    {screenMode === "lg" && (
                        <div className="d-flex ms-auto">
                            {/* Panel and Login Button */}
                            <button
                            className="btn btn-success rounded-end-0 rounded-start-3 border-contrast"
                            type="button"
                            aria-label={isLogin ? "Go to Control Panel" : "Got to Login page"}
                            title={isLogin ? "Control Panel" : "Login"}
                            >
                                {isLogin ? <><i className="fas fa-user me-2" aria-hidden="true"></i> Panel</> : <><i className="fas fa-user me-2" aria-hidden="true"></i> Login</>}
                            </button>

                            {/* Cart Button */}
                            <button
                            className="btn btn-success rounded-end-3 rounded-start-0 border-contrast"
                            type="button"
                            aria-label="View Shopping Cart"
                            title="Shopping Cart"
                            disabled={!isLogin}
                            >
                            <i className="fas fa-cart-shopping me-2" aria-hidden="true"></i> Cart
                            </button>
                        </div>
                    )}

                
                </div>
            </nav>
            
            {/* Bottom Navbar */}
            { screenMode !== "lg" && screenMode !== "lt" ? (
                <nav className="navbar bg-transparent border-bottom border-light fixed-bottom p-0 py-0">
                    <div className="container-fluid d-flex align-items-center p-0 py-0">
                        <button className="btn bg-contrast rounded-0 border-0 flex-fill d-flex flex-column justify-content-center align-items-center text-body" style={{ height: "80px" }}>
                            {isLogin ? <><i className="fas fa-user mb-2" aria-hidden="true"></i> Panel</> : <><i className="fas fa-user mb-2" aria-hidden="true"></i> Login</>}
                        </button>
                        <button className="btn bg-contrast rounded-0 border-0 flex-fill d-flex flex-column justify-content-center align-items-center text-body" disabled={!isLogin} style={{ height: "80px" }}>
                            <i className="fas fa-cart-shopping fa-lg mb-3"></i>
                            My Cart
                        </button>                        
                    </div>
                </nav>
            ) : null}

            <ThemeToggleButton screenMode={screenMode} />

        
        </>
    );
}

export default MainNavbar;
