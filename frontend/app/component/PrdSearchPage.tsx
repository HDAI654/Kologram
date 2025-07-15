"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import { useEffect, useState, useRef } from "react";
import Loading_component from "./Loading";
import axios from "axios";
import baseURL from "../BaseURL";
import { toast } from 'react-toastify';
import Product from "./Product";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;


function PrdSeachPage({ searchValue, setSearchValue }: { searchValue: string, setSearchValue: React.Dispatch<React.SetStateAction<string>> }) {
    const [load, setLoad] = useState(false);
    const [products, setProducts] = useState<any[]>([]);
    const [error, setError] = useState("");
    const page = useRef(0);
    const isFetchingPrds = useRef(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const hasMorePrd = useRef(true);



    useEffect(() => {
        page.current = 0;
        hasMorePrd.current = true;
        setProducts([]);
        setError("");
        setLoad(false);

        const { searchTextOnly, category} = getCategoryAndText(searchValue);
        getPrds(searchTextOnly, category);
        }, [searchValue]
    );


    const getCategoryAndText = (search: string) => {
        // separation category and search text with split :
        const searchText = search.split(":", 2);
        let category = searchText.length > 1 ? searchText[0] : "";
        let searchTextOnly = searchText.length > 1 ? searchText[1] : searchText[0];
        return { searchTextOnly, category};
    };


    // get products from server
    const getPrds = async (search: string, category: string) => {
        console.log("Loading page:", page.current);
        if (isFetchingPrds.current) return;
        if (!hasMorePrd.current) return;
        isFetchingPrds.current = true;


        if (!search || search.trim() === "") {
            return;
        }

        try {
            const res = await axios.get(`/prd-api/search-prd?search_text=${search}${category ? "&category=" + category : ""}&page=${page.current}`);
            if (res.data.products.length === 0 && page.current === 0) {
                setError("No products found !");
            }
            if (res.data.products.length === 0 && page.current > 0) {
                console.log("No more products");
                hasMorePrd.current = false;
                return;
            }
            setProducts(prevProducts => [...prevProducts, ...res.data.products]);
            page.current++;
            console.log(res.data.products);
            
        } catch (err : any) {
            if (err.response && err.response.status === 400) {
                toast.error("Invalid data !");
                setSearchValue("");
            } else {
                toast.error("Something went wrong. Try again.");
                setSearchValue("");
            }
        } finally {
            setLoad(true);
            isFetchingPrds.current = false;
        }
    };

    const handleScroll = () => {
        const container = scrollRef.current;
        if (!container) return;

        const scrollTop = container.scrollTop;
        const scrollHeight = container.scrollHeight;
        const clientHeight = container.clientHeight;

        // if 100 pixels from the bottom, fetch more data
        if (scrollTop + clientHeight >= scrollHeight - 100) {
            if (!hasMorePrd.current) {
                return;
            }
            const { searchTextOnly, category} = getCategoryAndText(searchValue);
            getPrds(searchTextOnly, category);
        }
    };

    if (load === false) {
        return <Loading_component />;
    }

    return (
        <>
            {error === "" ? (
                <div 
                    className="container-fluid justify-content-center align-items-start"
                    style={{ 
                        maxHeight: "calc(100vh - 90px)", 
                        overflowY: "auto", 
                        paddingTop: "90px"
                    }}
                    onScroll={handleScroll}
                    ref={scrollRef}
                >
                    
                    <div className="row">
                        {products.map((product:any, index:number) => (
                            <Product key={index} info={product} />
                        ))}
                    </div>

                </div>
            ) : (
                <div className="container-fluid vh-100 d-flex justify-content-center align-items-center">
                    <h2 className="mt-5 text-wrap">{error}</h2>
                </div>
            )}
        </>

    );
}

export default PrdSeachPage;
