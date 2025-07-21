import React from "react";
import Sidebar from "./DrawerMenu";
import ThemeToggleButton from "./ThemeNavbar";
import NavSearch from "./NavSearch";
import Link from "next/link";


const isLogin = true;
const username = "Guest";

function MainNavbar() {
    return (
        <>

            {/* Top Navbar */}
            <nav
                className="navbar border-0 bg-contrast bg-body fixed-top"
                style={{ zIndex: 1000, height: "50px", padding: 0 }}
            >
                <div
                    className="container-fluid d-flex justify-content-between align-items-center"
                    style={{ height: "100%" }}
                >
                    {/* Brand Logo */} 
                    <Link href="/" aria-label="Kologram Home Page" title="Kologram Home Page" className="btn btn-link text-body d-flex align-items-center" style={{ textDecoration: "none", height: "100%" }}>
                    <svg
                        aria-hidden="true"
                        focusable="false"
                        viewBox="0 0 24 24"
                        role="img"
                        width="60px"
                        height="60px"
                        fill="none"
                    >
                        <path
                        fill="currentColor"
                        d="M4 13c1.5 3 4.5 4.5 8 4.5s6.5-1.5 8-4.5c.2-.4.2-.8-.1-1.1-.3-.3-.8-.3-1.1 0-1.2 2.5-3.7 3.6-6.8 3.6s-5.6-1.1-6.8-3.6c-.2-.4-.7-.5-1.1-.2-.3.3-.4.7-.1 1.1z"
                        />
                    </svg>
                    <span className="visually-hidden">Kologram</span>
                    </Link>

                    {/* Controls */}
                    <div className="d-flex align-items-center gap-2 h-100">

                        {/* Search Bar */}
                        <NavSearch />

                        {/* Panel/Login Button */}
                        <button
                            className="btn bg-transparent border-0 text-body d-flex align-items-center"
                            type="button"
                            title={isLogin ? "Control Panel" : "Login"}
                            aria-label={isLogin ? "Go to Control Panel" : "Go to Login Page"}
                        >
                            <i className="fas fa-user fa-lg" />
                        </button>

                        {/* Cart Button */}
                        <button
                            className="btn bg-transparent border-0 text-body d-flex align-items-center"
                            type="button"
                            title="Shopping Cart"
                            aria-label="View Shopping Cart"
                            disabled={!isLogin}
                        >
                            <i className="fas fa-cart-shopping fa-lg" />
                        </button>

                        {/* Menu Button */}
                        <button
                            className="btn text-body fs-4 fa-lg d-flex align-items-center"
                            data-bs-toggle="offcanvas"
                            data-bs-target="#sidebarMenu"
                        >
                            ☰
                        </button>
                    </div>
                </div>
            </nav>


            {/* Menu */}
            <Sidebar username={username} />

            {/* Theme Toggle */}
            <ThemeToggleButton />

        </>
    );
}

export default MainNavbar;
