"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import { useEffect, useState } from "react";
import axios from "axios";
import baseURL from "../BaseURL";
import defaultImage from "../DefaultImage";
import "@/public/myPrd.css";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function MyProductPage() {
  const [myPrd, setMyPrd] = useState([])
  const [errorSTS, seterrorSTS] = useState(false)
  const [isSmallScreen, setSmallScreen] = useState(0)

  useEffect(() => {
    const get_prds = async () => {
      try {
          const res = await axios.get(`/prd-api/get_products?by_user=1`);
          const prds = res.data.products
          if (prds === false) {
              seterrorSTS(true);
              return; 
          } else {
            setMyPrd(prds)
            return; 
          }
      } catch (err : any) {
          seterrorSTS(true);
          return; 
      }
    }
    get_prds();

    handleResize();
    window.addEventListener("resize", handleResize)
  }, []);

  const handle_prd_click = (id:number) => {
    if (!id) {return;}
    try {
      window.open(`/products/view/?id=${id}`, '_blank');
    } catch (err : any) {
      toast.error("Something went wrong. Try again.");
      return;
    }
  };

  const handleEditClick = (id:number) => {
    console.log(String(id))
  };

  const handleResize = () => {
    let width = window.innerWidth
    if (width < 320) {
      setSmallScreen(2);
      return;
    }else if (width < 560) {
      setSmallScreen(1);
      return;
    }else {
      setSmallScreen(0);
      return;
    }
  }

  const chunkedProducts = [];
  for (let i = 0; i < myPrd.length; i += 2) {
    chunkedProducts.push(myPrd.slice(i, i + 2));
  }
  if (errorSTS === true) return (<h1 className="mt-5 text-light text-center">Error in found your products</h1>)

  return (
    <>
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
      <div className="container">

        {chunkedProducts.map((group, rowIndex) => (
          <div className="row w-100" key={rowIndex}>
            {group.map((v, i) => (
              <div className={`col-lg-6 col-md-12 col-sm-12 py-2 d-flex align-items-center rounded-5 mt-3 bg-light ${isSmallScreen === 2 && "justify-content-center"}`} id="myprd_div" key={i}>
                { isSmallScreen!==2 && <img
                  src={v.image === null ? defaultImage : baseURL + v.image}
                  className="img-fluid ml-1"
                  alt={v.name || "product image"}
                  style={{ height: "10vh", objectFit: "contain" }}
                /> }

                <h5 className={`card-title text-primary text-wrap ml-3 ${isSmallScreen === 2 && 'text-center justify-content-center'}`}>
                  {v.name}
                  {isSmallScreen > 0 && <br />}
                  <span className="badge bg-success text-light rounded-5 text-wrap ms-2" style={{cursor:"pointer"}} onClick={() => handleEditClick(v.id)}>
                    Show/Edit
                  </span>
                  <span className="badge bg-primary text-light rounded-5 text-wrap ms-2" style={{cursor:"pointer"}} onClick={() => handle_prd_click(v.id)}>
                    Open
                  </span>
                </h5>
    
              </div>
            ))}
          </div>
        ))}

      </div>
    </>
  );
}

export default MyProductPage;
