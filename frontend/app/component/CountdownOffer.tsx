'use client';
import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import Countdown from 'react-countdown';
import baseURL from '@/app/BaseURL';
import "@/public/CountdownOffer.css";

interface Offer {
  title: string;
  description: string;
  link: string | null;
  end_time: string;
}

function Countdown_ctm({offer}:{offer:Offer}){
    const renderer = ({ days, hours, minutes, seconds, completed }: any) => {
    if (completed) {
      return (
        <div className="d-flex justify-content-center text-danger fw-bold">
          Expired
        </div>
      );
    }

    return (
      <div className="d-flex justify-content-center gap-2">
        <TimeBox value={days} label="Days" />
        <TimeBox value={hours} label="Hours" />
        <TimeBox value={minutes} label="Minutes" />
        <TimeBox value={seconds} label="Seconds" />
      </div>
    );
  };

  const TimeBox = ({ value, label }: { value: number; label: string }) => (
    <div
      className="text-center bg-light border rounded p-2 shadow-sm"
      style={{ minWidth: '35px' }}
    >
      <div className="fs-4 fw-bold text-primary shadow-lg">{value}</div>
      <div className="small text-dark">{label}</div>
    </div>
  );

  return (
    <div 
      className="offer-card"
      style={{ 
        minWidth: '320px', 
        maxWidth: '320px', 
        flexShrink: 0 
      }}
    >
        <div className="card h-100 shadow-sm">
            <div className="card-body d-flex flex-column">
            <h5 className="card-title">{offer.title}</h5>
            <p className="card-text text-muted">{offer.description}</p>
            {offer.link && (
                <a
                href={offer.link}
                className="btn btn-outline-primary btn-sm mt-auto mb-3"
                >
                Learn More
                </a>
            )}
            <div className="alert alert-info text-center mb-0">
                <Countdown
                date={new Date(offer.end_time)}
                renderer={renderer}
                />
            </div>
            </div>
        </div>
    </div>
  );
    

}

function CountdownOffer() {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [cardWidth, setCardWidth] = useState<number>(320);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [screenMode, setScreenMode] = useState("lt");

  useEffect(() => {
    handleResize();
    window.addEventListener("resize", handleResize);
    
    // calculate width of each offer card
    const updateWidth = () => {
      setCardWidth(window.innerWidth > 1200 ? 320 : window.innerWidth > 768 ? 280 : 250);
    };
    updateWidth();
    window.addEventListener("resize", updateWidth);
    
    // get offers
    const getOffers = () => {
      axios
        .get(baseURL + '/ad/get-offers/')
        .then((res) => {
          setOffers(res.data);
        })
        .catch((err) => {
          console.error('Failed to fetch offers:', err);
        });
    };
    getOffers();
    
    // Setup wheel scrolling
    const scrollContainer = scrollRef.current;
    if (scrollContainer) {
      const handleWheel = (e: WheelEvent) => {
        if (e.deltaY !== 0) {
          e.preventDefault();
          scrollContainer.scrollLeft += e.deltaY * 0.5;
        }
      };
      
      scrollContainer.addEventListener('wheel', handleWheel, { passive: false });
      
      return () => {
        window.removeEventListener("resize", handleResize);
        window.removeEventListener("resize", updateWidth);
        scrollContainer.removeEventListener('wheel', handleWheel);
      };
    }
    
    return () => {
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("resize", updateWidth);
    };
  }, []);

  const handleResize = () => {
    let width = window.innerWidth;
    if (width < 400) {
      setScreenMode("lt");
      return;
    } else if (width < 600) {
      setScreenMode("sm");
      return;
    } else if (width < 1000) {
      setScreenMode("md");
      return;
    } else {
      setScreenMode("lg");
      return;
    }
  };

  const scrollLeft = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: -cardWidth * 1.5, behavior: "smooth" });
    }
  };

  const scrollRight = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: cardWidth * 1.5, behavior: "smooth" });
    }
  };

  if (offers.length === 0) {
    return null;
  }

  return (
    <div className="mt-5 w-100 border-top py-3 mb-4 md:px-0 px-4">
      <div className="d-flex">
        <h3 className={`mb-4 ctm-hover mx-5 ${(screenMode === "lt" || screenMode === "sm") ? "text-center w-100" : "text-start"}`}>
          Active Offers
        </h3>
        {(screenMode === "lg" || screenMode === "md") && (
          <>
            <button className="scroll-btn me-1 bg-contrast text-body" aria-label="Prev" type="button" onClick={scrollLeft}>
              <svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" role="img" width="24px" height="24px" fill="none">
                <path stroke="currentColor" strokeWidth="1.5" d="M15.525 18.966L8.558 12l6.967-6.967" />
              </svg>
            </button>
            <button className="scroll-btn bg-contrast text-body" aria-label="Next" type="button" onClick={scrollRight}>
              <svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" role="img" width="24px" height="24px" fill="none">
                <path stroke="currentColor" strokeWidth="1.5" d="M8.474 18.966L15.44 12 8.474 5.033" />
              </svg>
            </button>
          </>
        )}
      </div>
      
      <div className="offers-scroll" ref={scrollRef}>
        {offers.map((offer, index) => (
          <Countdown_ctm offer={offer} key={index} />
        ))}
      </div>
    </div>
  );
}

export default CountdownOffer;
