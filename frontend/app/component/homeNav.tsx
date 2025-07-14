"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React, { useEffect } from "react";
import baseURL from "../BaseURL";
import { toast } from 'react-toastify';
import '@/public/entry-styles.css';
import ThemeNavbar from "./setThemeNavbar";
import Sidebar from "./DrawerMenu";
import NavButton from "./NavBarButton";
import '@/public/HomeNav.css';

function HomeNavbar({ screenMode, isLogin, username="Guest" }:{screenMode:string, isLogin:boolean, username:string}) {

    useEffect(() => {
        import("bootstrap/dist/js/bootstrap.bundle.min.js");
    }, []);

    const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault(); // Prevent the default form submission behavior
        const form = e.currentTarget;
        const formData = new FormData(form);
        const text = formData.get("search")
        toast.success("Search for " + text)
    };

    return (
        <>

            {/* Top Navbar */}
            <nav className="navbar border-0 border-bottom border-contrast bg-body fixed-top" style={{ height: "80px"}}>
                <div className="container-fluid d-flex align-items-center w-100">
                {screenMode !== "sm" && screenMode !== "lt" ? (
                    <a className="navbar-brand" href="#">
                        <img src="/NavIcon.svg" alt="Brand" style={{ objectFit: "cover", maxWidth: "150px", maxHeight: "80px" }} width="100%" height="100%" />
                    </a>
                ): null}

                <div className="d-flex flex-grow-1 align-items-center mx-3" style={{ maxWidth: "700px" }}>
                    <form className="d-flex flex-grow-1" onSubmit={handleSearch}>
                        <input
                            className={`form-control border-contrast ${screenMode !== "lt" ? "rounded-end-0 rounded-start-3 border-end-0" : null}`}
                            type="search"
                            placeholder="Search"
                            aria-label="Search"
                            name="search"
                            id="search"
                        />
                        { screenMode !== "lt" ? (
                            <button className="btn btn-success border-contrast border-start-0 rounded-end-3 rounded-start-0 me-3" type="submit">
                                Search
                            </button>
                        ) : null}
                    </form>

                    <Sidebar isLogin={isLogin} username={username} screenMode={screenMode} />
                </div>
                
                {screenMode === "lg" ? (
                    <div className="d-flex ms-auto">
                        <button className="btn btn-success rounded-start-3 rounded-end-0 border border-dark border-contrast">
                            Categories
                        </button>
                        <NavButton iconName="fa-cogs" text="Panel" buttonOtherClasses="rounded-0 border-contrast" disabled={!isLogin} />
                        <NavButton iconName="fa-cart-shopping" buttonOtherClasses="rounded-0 border-contrast" text="Cart" disabled={!isLogin} />
                        <NavButton iconName="fa-user" text="User" buttonOtherClasses="rounded-0 rounded-end-3 border-contrast" data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu" disabled={!isLogin} />
                    </div>
                ): null}
                
                </div>
            </nav>


            {/* Theme Navbar */}
            <ThemeNavbar screenMode={screenMode}/>
            
            {/* Bottom Navbar */}
            { screenMode !== "lg" && screenMode !== "lt" ? (
                <nav className="navbar bg-transparent border-bottom border-light fixed-bottom p-0 py-0" style={{ height: "80px" }}>
                    <div className="container-fluid d-flex align-items-center p-0 py-0">
                    <button className="btn btn-success border-contrast rounded-0 border-0 border-end flex-fill d-flex flex-column justify-content-center align-items-center" disabled={!isLogin} style={{ height: "80px" }}>
                        <i className="fas fa-cogs fa-lg mb-3"></i>
                        Panel
                    </button>
                    <button className="btn btn-success border-contrast rounded-0 border-0 border-end flex-fill d-flex flex-column justify-content-center align-items-center" disabled={!isLogin} style={{ height: "80px" }}>
                        <i className="fas fa-cart-shopping fa-lg mb-3"></i>
                        My Cart
                    </button>
                    <button className="btn btn-success border-contrast rounded-0 border-0 border-end flex-fill d-flex flex-column justify-content-center align-items-center" data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu" disabled={!isLogin} style={{ height: "80px" }}>
                        <i className="fas fa-user fa-lg mb-3"></i>
                        My Account
                    </button>
                    <button className="btn btn-success border-contrast rounded-0 border-0 flex-fill d-flex flex-column justify-content-center align-items-center" style={{ height: "80px" }}>
                        <i className="fas fa-bars fa-lg mb-3"></i>
                        Categories
                    </button>
                    </div>
                </nav>
            ) : null}

        
        </>
    );
}

export default HomeNavbar;
