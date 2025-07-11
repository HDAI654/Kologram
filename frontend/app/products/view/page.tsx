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
import { toast } from 'react-toastify';
import getCookie from "../../getCookie";
import '@/public/entry-styles.css';
import PrdComment from "../../component/prd-comment";

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
  const [comment, setComment] = useState([]);

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

    get_comments();

    handleResize();
    window.addEventListener("resize", handleResize)
  }, []);

  const get_comments = async () => {
      try {
        const res = await axios.get(`/prd-api/get-comments/?id=${id}`);
        const comments = res.data.comments;
        setComment(comments);
      } catch (err:any) {
        setComment([]);
        toast.error("Problem in fetching comments.");
      }
    }

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

  const handle_comment_add = async (e: React.FormEvent<HTMLFormElement>) => {
    try{
      setSubmitCommentLoad(true);
      e.preventDefault();
      const form = e.currentTarget;
      const formData = new FormData(form);

      const csrfToken = getCookie("csrftoken");
      const res = await axios.post(`/prd-api/add-comment/?prd_ID=${id}`, {"text": formData.get("comment"), "id":id}, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken
        }
      })
      toast.success("Comment added successfully");
    } catch (err:any) {
      if (err.response && err.response.status === 401) {
        toast.warn("Login required to add comments.");
      } else {
        toast.error("Something went wrong. Try again.");
      }
    } finally {
      setSubmitCommentLoad(false);
      get_comments();
    }
  }

  if (load === false) return <Loading_component />;
  if (!id && info === false) return <p style={{ color: "red" }}>Invalid product !!!</p>;

  return (
    <>
      < Sidebar />

      <div className="container-fluid py-4">
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
                <span className="badge bg-dark text-light rounded-5 text-wrap ms-2">
                  { info.condition }
                </span>
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
              
              <div className="text-left text-wrap text-dark border p-2" style={{maxHeight: "45vh", overflowY: "auto"}}>
                <ReactMarkdown>{info.description}</ReactMarkdown>
              </div>

          </div>
        </div>

        <div className="row px-3 rounded-bottom-5" style={{ backgroundColor: "#fff" }}>
          <h2 className="text-left text-dark text-wrap mt-3">Comments :</h2>

          {comment.map((comment, index) => (
            <div className="col-lg-4 col-md-12 col-sm-12 px-1 " key={index}>
              <PrdComment user={comment.user} text={comment.text} />
            </div>
          ))}

          {comment.length > 3 && <button className="btn btn-light w-100 text-wrap">Show all comments</button>}
          {comment.length === 0 && <h5 className="h5 w-100 text-wrap text-center">No comment to show !</h5>}

          <div className="col-lg-6 col-md-12 col-sm-12">
            <form className="form-group mt-5 mb-3 " onSubmit={handle_comment_add}>
              <label htmlFor="comment" className="text-dark text-wrap form-label h3">Leave a comment :</label>
              <textarea className="form-control text-wrap border-2 border-dark" id="comment" placeholder="Enter your comment about this product..." style={{minHeight: "200px"}} name="comment" required />    
              <button type="submit" className="btn btn-success w-100">Submit</button>
            </form>
          </div>
        </div>

      </div>
    </>
  );

}

export default Viewprd;
