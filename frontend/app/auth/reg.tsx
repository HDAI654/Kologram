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

function Reg_component({setPage}:{setPage:Function}) {
  const [confirm, setConfirm] = useState(false);
  const [passwords, setPasswords] = useState("");
  const [load, setLoad] = useState(false);
  const router = useRouter();

  useEffect(() => {
    document.title = "Kologram - Register";

    axios.get("/auth/get_auth/")
      .then((res) => {
        if (res.data.auth === true) {
          router.push("/");
        } else {
          setLoad(true);
        }
      })
      .catch((err) => {
        setLoad(false)
        toast.error("Something went wrong. Please try again.");
      });
  }, []);



  const handle_reg = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault(); // Prevent the default form submission behavior

    const form = e.currentTarget;
    const formData = new FormData(form);
    const data = {
      username: formData.get("username"),
      password: formData.get("password"),
      email: formData.get("email"),
    };

    try {
      const csrfToken = getCookie("csrftoken");
      const res = await axios.post("/auth/reg/", data, {
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken},
      });

      if (res.data.reg === true) {
        router.push("/");
      } else if (res.data.reg === "EXISTS") {
        toast.error("Username already exists !");
      }else {
        toast.error("Invalid data provided !");
      }
    } catch (err:any) {
      if (err.response && err.response.status === 409) {
        toast.error("Username already exists !");
      } else if (err.response && err.response.status === 422) {
        toast.error("Invalid data provided !");
      } else {
        toast.error("Something went wrong. Try again.");
      }
    }
  };

  const confirm_handle = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;

    setPasswords((prev) => ({
      ...prev,
      [name]: value,
    }));

    if (name === "password" || name === "confirm_password") {
      const pass = name === "password" ? value : passwords.password;
      const confirmPass = name === "confirm_password" ? value : passwords.confirm_password;
      setConfirm(pass === confirmPass && pass !== "");
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

            <h1 className="text-center text-light mt-4">Register</h1>
            <form onSubmit={handle_reg} method="post" className="px-3">
              <div className="form-group">
                <label htmlFor="username" className="form-label text-light mt-4 text-wrap" > Username </label>
                <input type="text" className="form-control mb-3 text-wrap" id="username" placeholder="Enter your username" name="username" required />

                <label htmlFor="password" className="form-label text-light text-wrap"> Password </label>
                <input type="password" className="form-control mb-3 text-wrap" id="password" placeholder="Enter your password" name="password" onChange={confirm_handle} required />

                <label htmlFor="confirm_password" className="form-label text-light text-wrap"> Confirm Password </label>
                <input type="password" className="form-control mb-3 text-wrap" id="confirm_password" placeholder="Confirm your password" name="confirm_password" onChange={confirm_handle} required />

                <label htmlFor="email" className="form-label text-light text-wrap"> Email </label>
                <input type="email" className="form-control mb-3 text-wrap" id="email" placeholder="Enter your email" name="email" required />

                <button type="submit" className="btn btn-primary mt-2 w-100" disabled={(confirm===false) ? true : false}> Register </button>
              </div>
            </form>

          </div>

          <div className="text-center mb-4 px-3">

            <hr className="text-light" />
            <h5 className="text-primary" onClick={(() => {setPage("0")})} style={{cursor: "pointer"}}> Back to Login </h5>

          </div>

        </div>
      </div>
    </div>
  );
}

export default Reg_component;
