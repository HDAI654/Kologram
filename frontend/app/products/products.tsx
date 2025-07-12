"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import baseURL from "../BaseURL";
import Loading_component from "../component/Loading";
import Prd from "../component/prd";
import Sidebar from "../component/DrawerMenu";
import { toast } from 'react-toastify';

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function Products() {
  const [error, setError] = useState("");
  const [load, setLoad] = useState(false);
  const [products, setProducts] = useState<any[]>([]);
  const [page, setPage] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [searhTXT, setSearchTXT] = useState("");
  const [isSearching, setSearching] = useState("0");
  const [isDelShow, setDelShow] = useState(false);
  const isFetching = useRef(false);
  const isSearchClicked = useRef(false);

  const fetchProducts = async () => {
    if (isFetching.current || !hasMore) return;
    isFetching.current = true;

    try {
      const url = isSearching === "0" ? `/prd-api/get_products?page=${page}` : `/prd-api/get_products?page=${page}&search=1&search_text=${searhTXT}`
      const res = await axios.get(url);
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
    if (products.length === 0) {
      fetchProducts();
    }
  }, [products]);

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

  const handleSearchChange = (v) => {
    setSearchTXT(v.target.value)
    isSearchClicked.current = true;
  };

  const handleSearchClick = () => {
    if (isSearchClicked.current === false){
      toast.warning("Your search already is showing")
    }else if (searhTXT !== ""){
      setPage(0)
      setProducts([])
      setSearching("1")
      setHasMore(true)
      setDelShow(true)
      isSearchClicked.current = false;
    } else {
      toast.error("Please fill the search input to search")
    }
  };

  const handleDelSearchClick = () => {
    setPage(0)
    setSearchTXT("")
    setProducts([])
    setSearching("0")
    setHasMore(true)
    setDelShow(false)
  };

  if (load === false) return <Loading_component />;

  const chunkedProducts = [];
  for (let i = 0; i < products.length; i += 3) {
    chunkedProducts.push(products.slice(i, i + 3));
  }

  return (
  <>
    <Sidebar />
    <div className="container-fluid py-3">
      {error && <div className="alert alert-danger text-center h1 text-wrap" role="alert">Error : {error}</div>}
      <div className="input-group p-4 mb-3 text-wrap">
        <input type="text" className={`form-control text-wrap ${(isDelShow && searhTXT.length !== 0) ? 'rounded-0 rounded-start-3' : ''}`} placeholder="Search ..." onChange={handleSearchChange} value={searhTXT} />
          {isDelShow && <button className="btn btn-danger rounded-0" onClick={handleDelSearchClick}>⛒</button>}
          {searhTXT.length !== 0 && <button className="btn btn-success rounded-0 rounded-end-3" onClick={handleSearchClick}>Search</button>}
      </div>

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
                likes={product.likes}
                condition={product.condition}
              />
            </div>
          ))}
        </div>
      ))}


    </div>
  </>
);

}

export default Products;
