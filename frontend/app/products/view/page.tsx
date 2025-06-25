"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React, { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Loading_component from "../../component/Loading";
import axios from "axios";
import baseURL from "../../BaseURL";
import defaultImage from "../../DefaultImage";
import Sidebar from "../../component/DrawerMenu";
import ReactMarkdown from "react-markdown";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import getCookie from "../../getCookie";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function Viewprd() {

  const searchParams = useSearchParams();
  const id = searchParams.get("id");
  const [load, setLoad] = useState(false);
  const [info, setInfo] = useState(false);
  const [starred, setStarred] = useState("DISABLED");
  const [inCart, setInCart] = useState("DISABLED");
  const [liked, setLiked] = useState("DISABLED");
  const [submitCommentLoad, setSubmitCommentLoad] = useState(false);

  useEffect(() => {
    const bootstrapInit = async () => {
      await import("bootstrap/dist/js/bootstrap.bundle.min.js");
    };
    bootstrapInit();

    const get_info = async () => {
      try {
          const res = await axios.get(`/prd-api/get_products?id=${id}`);
          const prd_info = res.data.products[0];
          if (prd_info === false) {
              setInfo(false);
              setLoad(true);
              return; 
          } else {
              prd_info.image = prd_info.image !== null && baseURL + prd_info.image
              setInfo(prd_info);
              setLoad(true);
              document.title = prd_info.name || "Product Details";
              return; 
          }
      } catch (err : any) {
          setInfo(false);
          setLoad(true);
          return; 
      }
    }
    get_info();

    const check_starred = async () => {
      try {
        const res = await axios.get(`/prd-api/is-starred/?prd_ID=${id}`);
        const hs = res.data.has_starred;

        if (hs === true) {
          setStarred("YES");
        } else if (hs === false) {
          setStarred("NO");
        } else if (hs === "NO_LOGIN") {
          setStarred("NO_LOGIN");
        } else {
          setStarred("DISABLED");
        }
      } catch (err:any) {
        if (err.response && err.response.status === 401) {
          setStarred("NO_LOGIN");
        } else {
          setStarred("DISABLED");
        }
      }
    };
    check_starred();

    const check_inCart = async () => {
      try {
        const res = await axios.get(`/prd-api/is-inCart/?prd_ID=${id}`);
        const sts = res.data.status;

        if (sts === true) {
          setInCart("YES");
        } else if (sts === false) {
          setInCart("NO");
        } else if (sts === "NO_LOGIN") {
          setInCart("NO_LOGIN");
        } else {
          setInCart("DISABLED");
        }
      } catch (err:any) {
        if (err.response && err.response.status === 401) {
          setInCart("NO_LOGIN");
        } else {
          setInCart("DISABLED");
        }
      }
    };
    check_inCart();

    const check_liked = async () => {
      try {
        const res = await axios.get(`/prd-api/is-liked/?prd_ID=${id}`);
        const hs = res.data.status;

        if (hs === true) {
          setLiked("YES");
        } else if (hs === false) {
          setLiked("NO");
        } else if (hs === "NO_LOGIN") {
          setLiked("NO_LOGIN");
        } else {
          setLiked("DISABLED");
        }
      } catch (err:any) {
        if (err.response && err.response.status === 401) {
          setLiked("NO_LOGIN");
        } else {
          setLiked("DISABLED");
        }
      }
    };
    check_liked();

    handleResize();
    window.addEventListener("resize", handleResize)
  }, []);

  const handle_star_click = async () => {
    if (starred === "NO_LOGIN") {
      toast.warn("Login required to rate products.");
      return;
    } else if (starred === "DISABLED") {
      toast.error("Something went wrong. Try again.");
      return;
    }

    try {
      setStarred("LOADING")
      const opt = starred === "YES" ? "DEL" : "ADD";
      const csrfToken = getCookie("csrftoken");
      const res = await axios.post(`/prd-api/chn-star/?opt=${opt}&prd_ID=${id}`, {}, {
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            }
          });

      if (res.data.status === "OK") {
        setStarred(opt === "ADD" ? "YES" : "NO");

        setInfo(prev => ({
          ...prev,
          stars: opt === "ADD" ? prev.stars + 1 : Math.max(prev.stars - 1, 0),
        }));

        toast.success(opt === "ADD" ? "Star added." : "Star removed.");
      } else if (res.data.status === "NO_LOGIN") {
        toast.error("Login required to rate products.");
      } else {
        toast.error("Something went wrong. Try again.");
      }

    } catch (err : any) {
      if (err.response && err.response.status === 401) {
        toast.warn("Login required to rate products.");
      } else {
        toast.error("Something went wrong. Try again."); 
      }
    }
  };

  const handle_Cart_click = async () => {
    if (inCart === "NO_LOGIN") {
      toast.warn("Login required to add products to your cart.");
      return;
    } else if (inCart === "DISABLED") {
      toast.error("Something went wrong. Try again.");
      return;
    }

    try {
      setInCart("LOADING")
      const opt = inCart === "YES" ? "DEL" : "ADD";
      const csrfToken = getCookie("csrftoken");
      const res = await axios.post(`/prd-api/chn-inCart/?opt=${opt}&prd_ID=${id}`, {}, {
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            }
          });

      if (res.data.status === "OK") {
        setInCart(opt === "ADD" ? "YES" : "NO");

        toast.success(opt === "ADD" ? "added successfully" : "removed successfully");
      } else if (res.data.status === "NO_LOGIN") {
        toast.error("Login required to add products to your cart.");
      } else {
        toast.error("Something went wrong. Try again.");
      }

    } catch (err : any) {
      if (err.response && err.response.status === 401) {
        toast.warn("Login required to add products to your cart.");
      } else {
        toast.error("Something went wrong. Try again."); 
      }
    }
  };

  const handle_like_click = async () => {
    if (liked === "NO_LOGIN") {
      toast.warn("Login required to like products.");
      return;
    } else if (liked === "DISABLED") {
      toast.error("Something went wrong. Try again.");
      return;
    }

    try {
      console.log(info.image)
      setLiked("LOADING")
      const opt = liked === "YES" ? "DEL" : "ADD";
      const csrfToken = getCookie("csrftoken");
      const res = await axios.post(`/prd-api/chn-like/?opt=${opt}&prd_ID=${id}`, {}, {
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken
            }
          });

      if (res.data.status === "OK") {
        setLiked(opt === "ADD" ? "YES" : "NO");

        setInfo(prev => ({
          ...prev,
          likes: opt === "ADD" ? prev.likes + 1 : Math.max(prev.likes - 1, 0),
        }));

        toast.success(opt === "ADD" ? "Liked successful" : "like removed.");
      } else if (res.data.status === "NO_LOGIN") {
        toast.error("Login required to like products.");
      } else {
        toast.error("Something went wrong. Try again.");
      }

    } catch (err : any) {
      if (err.response && err.response.status === 401) {
        toast.warn("Login required to like products.");
      } else {
        toast.error("Something went wrong. Try again."); 
      }
    }
  };

  const handleResize = () => {
    let width = window.innerWidth
    if (width < 768) {
      console.log("0");
    } else {
      console.log("1");
    }
  }

  if (load === false) return <Loading_component />;
  if (!id && info === false) return <p style={{ color: "red" }}>Invalid product !!!</p>;

  return (
    <>
      < Sidebar />

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

      <div className="container py-4">
        <div className="row rounded-top-5" style={{ backgroundColor: "#fff" }}>
          <div className="col-lg-6 col-md-12 col-sm-12 p-3">
            <img
                src={info.image || defaultImage}
                className="img-fluid w-100"
                alt={info.name || "product image"}
                style={{ height: "50vh", objectFit: "contain" }}
              />
          </div>

          <div className="col-lg-6 col-md-12 col-sm-12 p-3 text-left">
              <h2 className="text-primary mt-4 text-wrap">
                {info.name} 
                <span
                  className="badge bg-dark rounded-5 text-wrap ms-2"
                  style={{ cursor: starred === "DISABLED" ? "not-allowed" : "pointer" }}
                  aria-disabled={starred === "DISABLED"}
                  onClick={handle_star_click}
                >
                  {starred === "LOADING" ? (
                    <span
                      className="spinner-border spinner-border-sm text-light"
                      role="status"
                      aria-hidden="true"
                    ></span>
                  ) : (
                    <>
                      {starred === "YES" ? "⭐" : "★"} {info.stars}
                    </>
                  )}
                </span>
                <span
                  className="badge bg-dark rounded-5 text-wrap ms-2"
                  style={{ cursor: starred === "DISABLED" ? "not-allowed" : "pointer" }}
                  aria-disabled={starred === "DISABLED"}
                  onClick={handle_like_click}
                >
                  {liked === "LOADING" ? (
                    <span
                      className="spinner-border spinner-border-sm text-light"
                      role="status"
                      aria-hidden="true"
                    ></span>
                  ) : (
                    <>
                      {liked === "YES" ? "♥️" : "🤍"} {info.likes}
                    </>
                  )}
                </span>
              </h2>

              <h5 className="text-left text-wrap text-dark">
                {info.price} {info.currency_type} 
                <span className="badge bg-warning text-dark rounded-5 text-wrap ms-2" style={{ cursor: "pointer" }} onClick={handle_Cart_click}>
                  {inCart === "LOADING" ? (
                    <span
                      className="spinner-border spinner-border-sm text-light"
                      role="status"
                      aria-hidden="true"
                    ></span>
                  ) : (
                    <>
                      {inCart === "YES" ? "✅ Already in cart" : "Add to Cart"}
                    </>
                  )}
                </span>
              </h5>
              <hr className="text-dark"/>
              <h5 className="text-left text-wrap text-dark">About this item :</h5>
              
              <div className="text-left text-wrap text-dark">
                <ReactMarkdown>{info.description}</ReactMarkdown>
              </div>

          </div>
        </div>

        <div className="row rounded-bottom-5 border-top border-2 px-3" style={{ backgroundColor: "#fff" }}>
          <h2 className="text-left text-dark text-wrap mt-3">Comments :</h2>

          <form className="form-group mt-3 mb-3">
            <label htmlFor="comment" className="text-dark text-wrap form-label">Leave a comment :</label>
            <div className="input-group">
                <input type="text" className="form-control text-wrap" id="comment" placeholder="Enter your comment about this product..." name="comment" required />
                <button type="submit" className="btn btn-success">Submit</button>
            </div>
          </form>
        </div>


      </div>
    </>
  );

}

export default Viewprd;
