"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import { useEffect, useState } from "react";
import axios from "axios";
import baseURL from "./BaseURL";
import { useRouter } from "next/navigation";
import Loading_component from "./component/Loading";
import Sidebar from "./component/DrawerMenu";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

export default function Home() {
  const router = useRouter();
  const [load, setLoad] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    document.title = "Kologram - Home";

    axios.get("/auth/get_auth/")
    .then((res) => {
      if (res.data.auth === false) {
        router.push(`/auth`);
      } else {
        setLoad(true);
      }
    })
    .catch((err) => setLoad(false));
    
  }, []);


  if (load === false) {
    return (
      <Loading_component />
    );
  }

  return (
    <div className="container-fluid vh-100 bg-dark">
      <div className="row">
        < Sidebar />
        <h1 className="text-center mt-5 text-light">Home</h1>
        {error && <p className="text-center text-danger">{error}</p>}
      </div>
    </div>
  );
}
