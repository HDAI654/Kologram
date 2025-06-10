"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React, { useEffect, useState } from "react";
import axios from "axios";
import baseURL from "../BaseURL";
import { useRouter } from "next/navigation";
import Loading_component from "../component/Loading";
import Prd from "../component/prd";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function Products() {
  const [error, setError] = useState("");
  const [load, setLoad] = useState(false);
  const [products, setProducts] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const handleScroll = () => {
        const scrollTop = window.scrollY;
        const windowHeight = window.innerHeight;
        const fullHeight = document.documentElement.scrollHeight;

        if (scrollTop + windowHeight >= fullHeight - 10) {
            console.log('🚀 رسیدی به انتهای صفحه!');
        }
    }});


  
  if (load === false) {
    return (
      <Loading_component />
    );
  }
  
  return (
    <div className="container-fluid bg-dark w-100">
        {
            products.map((product, index) => (
                <Prd name={product.name} description={product.description} />
            ))
        }
    </div>
  );
}

export default Products;
