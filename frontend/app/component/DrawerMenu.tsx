"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import axios from "axios";
import baseURL from "../BaseURL";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import getCookie from "../getCookie";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

export default function Sidebar() {
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
              router.push("/auth/login/");
          } else {
              toast.error("Logout failed!");
          }
      } catch (err) {
        if (err.response && err.response.status === 401) {
          toast.error("You are not logged in, so you cannot log out.");
        } else {
          toast.error("Something went wrong. Try again.");
        }
      }
    };

  return (
    <div className="row">          
      <button className="btn text-light fs-1 m-3" style={{width:"65px"}} data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu"> ☰ </button>

      <div className="offcanvas offcanvas-start rounded-end-3 " tabIndex="-1" id="sidebarMenu">

        <ToastContainer
                position="top-right"
                autoClose={3000}
                hideProgressBar={false}
                newestOnTop={false}
                closeOnClick
                rtl={false}
                pauseOnFocusLoss
                draggable
                pauseOnHover
                theme="dark"
              />

        <div className="offcanvas-header">
          <h5 className="offcanvas-title ml-0">Menu</h5>
          <button type="button" className="btn-close" data-bs-dismiss="offcanvas"></button>
        </div>
        <div className="offcanvas-body">
          <ul className="list-unstyled">
            <li className="mt-2"><a href="/auth/login" className="nav-link">Login</a></li>
            <li className="mt-2"><span className="nav-link" onClick={handle_logout} style={{ cursor: "pointer" }}> Logout </span></li>
            <li className="mt-2"><a href="/products" className="nav-link">Products</a></li>
            <li className="mt-2"><a href="https://github.com/HDAI654" target="_blank" className="nav-link">About us</a></li>
          </ul>
        </div>
      </div>
    </div>
  );
}
