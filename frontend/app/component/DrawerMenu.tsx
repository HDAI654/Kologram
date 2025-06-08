"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import axios from "axios";
import baseURL from "../BaseURL";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function getCookie(name: string) {
  let cookieValue = null;
  if (typeof document !== "undefined" && document.cookie) {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const trimmed = cookie.trim();
      if (trimmed.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

export default function Sidebar({ setError }: { setError: React.Dispatch<React.SetStateAction<string>> }) {

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
                setError("Logout failed!");
            }
        } catch (err) {
            setError("Something went wrong. Please try again.");
        }
    };

  return (
    <>
      <button className="btn btn-light m-3" style={{width:"65px"}} data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu"> Menu </button>

      <div className="offcanvas offcanvas-start rounded-end-3 " tabIndex="-1" id="sidebarMenu">
        <div className="offcanvas-header">
          <h5 className="offcanvas-title ml-0">Menu</h5>
          <button type="button" className="btn-close" data-bs-dismiss="offcanvas"></button>
        </div>
        <div className="offcanvas-body">
          <ul className="list-unstyled">
            <li className="mt-2"><a className="nav-link" href="#" onClick={handle_logout}> Logout </a></li>
            <li className="mt-2"><a href="https://github.com/HDAI654" target="_blank" className="nav-link">About us</a></li>
          </ul>
        </div>
      </div>
    </>
  );
}
