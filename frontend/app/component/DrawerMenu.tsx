"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import axios from "axios";
import baseURL from "../BaseURL";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import getCookie from "../getCookie";
import { toast } from 'react-toastify';

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

export default function Sidebar({isLogin=false, username="Guest", screenMode}:{isLogin:boolean, username:string, screenMode:string}) {
    const router = useRouter();
    useEffect(() => {
        import("bootstrap/dist/js/bootstrap.bundle.min.js");
    }, []);

    const handle_logout = async () => {
      try {
          const csrfToken = getCookie("csrftoken");

          const res = await axios.post("/auth/logout/", {}, {
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            },
            withCredentials: true
          });

          if (res.data.logout === true) {
              router.push("/auth");
          } else {
              toast.error("Logout failed!");
          }
      } catch (err:any) {
        if (err.response && err.response.status === 401) {
          toast.error("You are not logged in, so you cannot log out.");
        } else {
          toast.error("Something went wrong. Try again.");
        }
      }
    };

  return (
    <div className="row">  
      { screenMode === "lt" && (
        <button className="btn fs-1 mx-3 text-body" style={{width:"65px"}} data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu"> ☰ </button>
      ) }        
      

      <div className={`offcanvas offcanvas-start rounded-end-3 ${ screenMode !== "lg" && screenMode !== "md" ? "w-100" : "w-50"}`} tabIndex="-1" id="sidebarMenu">
        {/* Header with user icon */}
        <div className="offcanvas-header flex-column align-items-start w-100 border-bottom">
          { screenMode === "lt" ? (
            <div className="d-flex align-items-center w-100"> 
              <i className="fas fa-user fa-lg me-2"></i>
              <span className="fs-5">{username}</span>
              <button
                  type="button"
                  className="btn-close"
                  data-bs-dismiss="offcanvas"
                  aria-label="Close"
                ></button>
            </div>
          ):(
            <>
            <button type="button" className="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            <div className="align-items-center d-flex justify-content-center w-100">
              <img src="http://localhost:8000/media/files/images/UNKNOWN.png" style={{ maxHeight:"200px", maxWidth:"200px", objectFit:"fill", borderRadius:"50%" }} width="100%" height="100%"></img>
            </div>
            <div className="d-flex justify-content-center align-items-center mt-3 w-100"> 
                <span className="fs-5">@{username}</span>
              </div>
            </>
          )}
          
        </div>

        {/* Body */}
        <div className="offcanvas-body px-3">
          <ul className="list-unstyled w-100">
            { screenMode !== "lt" ? (
              isLogin ? (
                  <li className="mt-3">
                    <span className="nav-link" onClick={handle_logout} style={{ cursor: "pointer" }}>
                      <i className="fas fa-sign-out-alt me-2"></i>Logout
                    </span>
                  </li>
                ): <li className="mt-3"><a href="/auth/login" className="nav-link"><i className="fas fa-sign-in-alt me-2"></i>Login</a></li>
            ) : (
              <>
                <li className="mt-3"><a href="/" className="nav-link"><i className="fas fa-home me-2"></i>Home</a></li>
                <li className="mt-3"><a href="/panel" className="nav-link"><i className="fas fa-cogs me-2"></i>Panel</a></li>
                {isLogin ? (
                  <li className="mt-3">
                    <span className="nav-link" onClick={handle_logout} style={{ cursor: "pointer" }}>
                      <i className="fas fa-sign-out-alt me-2"></i>Logout
                    </span>
                  </li>
                ): <li className="mt-3"><a href="/auth/login" className="nav-link"><i className="fas fa-sign-in-alt me-2"></i>Login</a></li>}

                <li className="mt-3"><a href="/products" className="nav-link"><i className="fas fa-boxes me-2"></i>Products</a></li>
                <li className="mt-3"><a href="/cart" className="nav-link"><i className="fas fa-shopping-cart me-2"></i>My Cart</a></li>
              </>
            )}
            
          </ul>
        </div>
      </div>

    </div>
  );
}
