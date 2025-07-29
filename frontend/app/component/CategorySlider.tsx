"use client";
import React, { useEffect, useState, useRef } from "react";
import "@/public/CategorySlider.css";
import axios from "axios";
import baseURL from "../BaseURL";
import defaultImage from "@/app/DefaultImage";
import { CATEGORY_IMAGES } from "../categories";
import Link from "next/link";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function CategorySlider() {
    const cardWidth = 320;
    const scrollRef = useRef<HTMLDivElement>(null);
    const [screenMode, setscreenMode] = useState("lt");

    useEffect(() => {
        handleResize();
        window.addEventListener("resize", handleResize);
        
        const scrollContainer = scrollRef.current;
        if (scrollContainer) {
            const handleWheel = (e: WheelEvent) => {
                if (e.deltaY !== 0) {
                    e.preventDefault();
                    scrollContainer.scrollLeft += e.deltaY;
                }
            };
            
            scrollContainer.addEventListener('wheel', handleWheel, { passive: false });
            
            return () => {
                scrollContainer.removeEventListener('wheel', handleWheel);
            };
        }
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

    return (
        <>
            <div className="mt-5 w-100 border-top mb-4 md:px-0 px-4">
                <div className="d-flex mt-3">
                    <h3 className={`mb-4 ctm-hover mx-5 ${(screenMode === "lt" || screenMode === "sm") ? "text-center w-100" : "text-start"}`}>
                        Categories
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

                <div className="ctg-scroll" ref={scrollRef}>
                    {CATEGORY_IMAGES.map((ctg, index) => (
                        <Link 
                        href={`/category/${ctg[0]}`} 
                        key={index} 
                        style={{textDecoration: "none", color: "inherit"}}
                        >
                            <div 
                            className="scale-in"
                            style={{ 
                                maxWidth: `${cardWidth}px`, 
                                minWidth: `220px`, 
                                width:"100%", 
                                flexShrink: 0, 
                                textAlign: "center" 
                            }}
                            >
                                <img
                                src={ctg[1] ? baseURL + ctg[1] : defaultImage}
                                alt={ctg[0]}
                                className="ctg-image ctg-hover"
                                />
                                <h2 className="ctg-name text-center ctm-hover">{ctg[0]}</h2>
                            </div>
                        </Link>
                    ))}
                </div>
            </div>
        </>
        
    );
}

export default CategorySlider;
