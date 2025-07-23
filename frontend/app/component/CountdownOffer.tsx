'use client';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Countdown from 'react-countdown';
import baseURL from '@/app/BaseURL';

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
      style={{ minWidth: '60px' }}
    >
      <div className="fs-4 fw-bold text-primary shadow-lg">{value}</div>
      <div className="small text-dark">{label}</div>
    </div>
  );

  return (
    <div className="col-md-6 col-lg-4">
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

  useEffect(() => {
    axios
      .get(baseURL + '/ad/get-offers/')
      .then((res) => {
        setOffers(res.data);
      })
      .catch((err) => {
        console.error('Failed to fetch offers:', err);
      });
  }, []);

  if (offers.length===0){
    return null;
  }

  return (
    <div className="container my-5">
      <h2 className="text-center mb-4">Active Offers</h2>
      <div className="row g-4">
        {offers.map((offer, index) => (
          <Countdown_ctm offer={offer} key={index} />
        ))}
      </div>
    </div>
  );
}

export default CountdownOffer;
