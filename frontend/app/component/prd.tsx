"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React, { useEffect } from "react";
import baseURL from "../BaseURL";
import defaultImage from "../DefaultImage";
import { toast } from 'react-toastify';
import '@/public/entry-styles.css';

interface PrdProps {
  prd_id: number;
  name: string;
  description: string;
  price: number;
  currency_type: string;
  image?: string;
  stars: number;
  likes: number;
  condition: string;
}

function Prd({ prd_id, name, description, price, currency_type, image, stars, likes, condition }: PrdProps) {
  if (image) {
    image = baseURL + image;
  }

  const handle_prd_click = () => {
    try {
      window.open(`/products/view/?id=${prd_id}`, '_blank');
    } catch (err : any) {
      toast.error("Something went wrong. Try again.");
      return;
    }
  };

  return (
    <div className="card rounded d-flex flex-column justify-content-between bg-light text-white combo-animate mx-auto" style={{ width: "100%", cursor: "pointer" }} onClick={handle_prd_click}>
      <img src={image || defaultImage} className="card-img-top img-fluid" alt={name || "product image"} style={{ height: "80%", objectFit: "cover" }}/>
      <div className="mb-1 mt-1 text-center text-dark">
        <h5 className="card-title text-wrap">
          {name}
          <span className="badge bg-dark rounded-5 text-wrap ms-2">
            {price} {currency_type}
          </span>
          <span className="badge bg-dark rounded-5 text-wrap ms-2">
            condition: {condition}
          </span>
          
        </h5>
      </div>
    </div>
  );
}

export default Prd;
