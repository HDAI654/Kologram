"use client";
import React, { useEffect, useState, useRef } from "react";
import "@/public/TopPrd.css";
import axios from "axios";
import baseURL from "../BaseURL";
import defaultImage from "@/app/DefaultImage";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function TopPrds() {
    const [prds, setPrds] = useState<any[]>([]);
    const [error, setError] = useState<boolean>(false);
    const [loading, setLoading] = useState<boolean>(true);
    const skeletonCount = 20;
    const [cardWidth, setCardWidth] = useState<number>(120);
    const scrollRef = useRef(null);
    const [screenMode, setscreenMode] = useState("lt");


    useEffect(() => {
        handleResize();
        window.addEventListener("resize", handleResize)
        
        // calculate width of each top product
        const updateWidth = () => {
            setCardWidth(window.innerWidth / 10);
        };
        updateWidth();
        
        // get top products
        const getTopPrds = async () => {
            try {
                const response = await axios.get("/prd-api/get-top-prds");
                const result = response.data?.result;

                if (!Array.isArray(result) || result.length === 0) {
                    setError(true);
                    return;
                }

                setPrds(result);
                setLoading(false);
            } catch (err) {
                console.error("Error fetching top products:", err);
                setError(true);
            }
        };
        getTopPrds();
    }, []);
    
    const handleResize = () => {
        let width = window.innerWidth
        if (width < 400) {
            setscreenMode("lt");
            return;
        }else if (width < 600) {
            setscreenMode("sm");
            return;
        }else if (width < 1000) {
            setscreenMode("md");
            return;
        }else {
            setscreenMode("lg");
            return;
        }
    };

    const scrollLeft = () => {
        if (scrollRef.current) {
        scrollRef.current.scrollBy({ left: -cardWidth * 2, behavior: "smooth" });
        }
    };

    const scrollRight = () => {
        if (scrollRef.current) {
        scrollRef.current.scrollBy({ left: cardWidth * 2, behavior: "smooth" });
        }
    };



    if (error) {
        return null;
    }

    return (
        <>
            {loading ? (
                <>
                    <div className="mt-5 w-100 border-top py-3 mb-4">
                        <div className="d-flex">
                            <h3 className="text-left mx-5 mb-4">
                                Top Products
                            </h3>
                            
                        </div>
                        <div className="top-prds-scroll" ref={scrollRef}>
                            {Array.from({ length: skeletonCount }).map((prd, index) => (
                                <div className="prd-card fade-in-up" key={index}>
                                    <img
                                        src={defaultImage}
                                        alt={"Top Product Image"}
                                        className="prd-image"
                                    />
                                    <p className="prd-name placeholder-glow">
                                        <span className="placeholder text-center w-100"></span>
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                </>
            ) : (
                <>
                    <div className="mt-5 w-100 border-top py-3 mb-4">
                        <div className="d-flex">
                            <h3 className="text-left mx-5 mb-4">
                                Top Products
                            </h3>
                            {(screenMode==="lg" || screenMode==="md") && (
                                <>
                                <button className="scroll-btn me-1 bg-contrast text-body scale-in" aria-label="Prev" type="button" onClick={scrollLeft}>
                                    <svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" role="img" width="24px" height="24px" fill="none">
                                        <path stroke="currentColor" strokeWidth="1.5" d="M15.525 18.966L8.558 12l6.967-6.967" />
                                    </svg>
                                </button>
                                <button className="scroll-btn bg-contrast text-body scale-in" aria-label="Next" type="button" onClick={scrollRight}>
                                    <svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" role="img" width="24px" height="24px" fill="none">
                                        <path stroke="currentColor" strokeWidth="1.5" d="M8.474 18.966L15.44 12 8.474 5.033" />
                                    </svg>
                                </button>
                                </>
                            )}
                            
                        </div>
                        <div className="top-prds-scroll" ref={scrollRef}>
                            {prds.map((prd, index) => (
                                <div 
                                 key={index}
                                 className="border pt-2 rounded-3 scale-in"
                                 style={{ 
                                    maxWidth: `${cardWidth}px`, 
                                    minWidth: `120px`, 
                                    width:"100%", 
                                    flexShrink: 0, 
                                    textAlign: "center" 
                                }}
                                 >
                                    <img
                                        src={prd.image ? baseURL + prd.image : defaultImage}
                                        alt={prd.name}
                                        className="prd-image"
                                    />
                                    <p className="prd-name mx-1">{prd.name}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </>
            )}
        </>
        
    );
}

export default TopPrds;
