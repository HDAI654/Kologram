"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import baseURL from "../BaseURL";
import Loading_component from "../component/Loading";
import Prd from "../component/prd";
import Sidebar from "../component/DrawerMenu";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function Products() {
  const [error, setError] = useState("");
  const [load, setLoad] = useState(false);
  const [products, setProducts] = useState<any[]>([]);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const isFetching = useRef(false);

  const fetchProducts = async () => {
    if (isFetching.current || !hasMore) return;
    isFetching.current = true;

    try {
      const res = await axios.get(`/prd-api/get_products?n=${page}`);
      const newProducts = res.data.products;

      if (!newProducts || newProducts.length === 0) {
        setHasMore(false);
        return;
      }
      setProducts((prev) => [...prev, ...newProducts]);
      setLoad(true);
      setPage((prev) => prev + 1);
    } catch (err) {
      setError("Error in getting data ! check your connection");
    } finally {
      isFetching.current = false;
    }
  };


  useEffect(() => {
    fetchProducts();
  }, []);

  const handleScroll = () => {
    const scrollTop = window.scrollY;
    const windowHeight = window.innerHeight;
    const fullHeight = document.documentElement.scrollHeight;

    if (scrollTop + windowHeight >= fullHeight - 10 && hasMore) {
      fetchProducts();
    }
  };

  useEffect(() => {
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [page, hasMore]);

  if (load === false) return <Loading_component />;

  const chunkedProducts = [];
  for (let i = 0; i < products.length; i += 3) {
    chunkedProducts.push(products.slice(i, i + 3));
  }

  return (
  <div style={{ minHeight: "100vh", backgroundColor: "#212529", color: "#fff" }}>
    <Sidebar />
    <div className="container-fluid py-3">
      {error && <div className="alert alert-danger text-center h1 text-wrap" role="alert">Error : {error}</div>}
      {chunkedProducts.map((group, rowIndex) => (
        <div className="row w-100" key={rowIndex}>
          {group.map((product, colIndex) => (
            <div
              className="col-lg-4 col-md-4 col-sm-12 mb-4 d-flex justify-content-center"
              key={colIndex}
              style={{ height: "55vh" }}
            >
              <Prd
                prd_id={product.id}
                name={product.name}
                description={product.description}
                price={product.price}
                currency_type={product.currency_type}
                image={product.image}
                stars={product.stars}
              />
            </div>
          ))}
        </div>
      ))}
    </div>
  </div>
);

}

export default Products;
