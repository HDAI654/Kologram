"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React, { useEffect, useState } from "react";
import axios from "axios";
import baseURL from "../BaseURL";
import { useRouter } from "next/navigation";
import Loading_component from "../component/Loading";
import { toast } from 'react-toastify';
import getCookie from "../getCookie";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function Login_component({setPage}:{setPage:Function}) {
  const [load, setLoad] = useState(false);
  const router = useRouter();

  useEffect(() => {
    document.title = "Kologram - Login";

    axios.get("/auth/get_auth/")
      .then((res) => {
        if (res.data.auth === true) {
          router.push("/");
        } else {
          setLoad(true);
        }
      })
      .catch((err) => {setLoad(false)
        toast.error("Something went wrong. Please try again.")
      });
  }, []);

  const handle_login = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // Prevent the default form submission behavior

    const form = e.currentTarget;
    const formData = new FormData(form);
    const data = {
      username: formData.get("username"),
      password: formData.get("password"),
    };

    try {
      const csrfToken = getCookie("csrftoken");
      const res = await axios.post("/auth/login/", data, {
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken},
      });

      if (res.data.login === true) {
        router.push("/");
      } else {
        toast.error("Invalid username or password");
      }
    } catch (err : any) {
        if (err.response && err.response.status === 422) {
          toast.error("Invalid data !");
        } else if (err.response && err.response.status === 401) {
          toast.error("Invalid username or password");
        }  else {
          toast.error("Something went wrong. Try again.");
        }
      }
  };

  
  if (load === false) {
    return (
      <Loading_component />
    );
  }
  
  return (
    <div className="container-fluid vh-100 bg-dark">
      <div className="row justify-content-center align-items-center min-vh-100">
        <div className="col-lg-4 col-md-6 col-sm-8 mx-auto mt-5 rounded-5 bg-dark d-flex flex-column justify-content-between" style={{ height: "80vh", boxShadow:"0px 0px 20px 2px rgba(255, 255, 255, 0.8)" }}>

          <div>

            <h1 className="text-center text-light mt-4">Login</h1>
            <form onSubmit={handle_login} method="post" className="px-3">
              <div className="form-group">
                <label htmlFor="username" className="form-label text-light mt-4 text-wrap" > Username </label>
                <input type="text" className="form-control mb-3 text-wrap" id="username" placeholder="Enter your username" name="username" required />

                <label htmlFor="password" className="form-label text-light text-wrap"> Password </label>
                <input type="password" className="form-control mb-3 text-wrap" id="password" placeholder="Enter your password" name="password" required />

                <button type="submit" className="btn btn-primary mt-2 w-100"> Login </button>
              </div>
            </form>

          </div>

          <div className="text-center mb-4 px-3">

            <hr className="text-light" />
            <h5 className="text-light">
              Don't have an account?{" "}
              <p className="text-primary" onClick={(() => {setPage("1")})} style={{cursor: "pointer"}}> Register here </p>
            </h5>

          </div>

        </div>
      </div>
    </div>
  );
}

export default Login_component;
