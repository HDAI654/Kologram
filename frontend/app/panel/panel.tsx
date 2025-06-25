"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import { useEffect, useState } from "react";
import axios from "axios";
import baseURL from "../BaseURL";
import { useRouter } from "next/navigation";
import Loading_component from "../component/Loading";
import Sidebar from "../component/DrawerMenu";
import MyProductPage from "../component/MyProductPage";
import AddProductPage from "../component/addProductPage";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function Panel() {
  const router = useRouter();
  const [load, setLoad] = useState(false);
  const [pagesHiddenSTS, setPagesHiddenSTS] = useState([true, true]);

  useEffect(() => {
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
    <>
      <Sidebar />
        <div className="container-fluid">
            <div className="row">
              <button className={`col-lg-6 col-md-6 col-sm-12 btn btn-${!pagesHiddenSTS[0] ? 'primary' : 'secondary'} text-wrap border-dark`} onClick={(() => setPagesHiddenSTS([false, true]))}>New Product</button>
              <button className={`col-lg-6 col-md-6 col-sm-12 btn btn-${!pagesHiddenSTS[1] ? 'primary' : 'secondary'} text-wrap border-dark`} onClick={(() => setPagesHiddenSTS([true, false]))}>My Products</button>
            </div>
        </div>

      <AddProductPage hidden={pagesHiddenSTS[0]}/>
      {pagesHiddenSTS[1] !== true && <MyProductPage />}
    </>
  )
}

export default Panel;
