"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import baseURL from "../BaseURL";
import defaultImage from "../DefaultImage";
import '@/public/entry-styles.css';

function Product({ info }: { info: any }) {

  return (
    <div className="col-12 col-md-6 col-lg-4 mb-4">
        <div 
            className="card h-100 shadow-sm cursor-pointer combo-animate" 
            style={{ borderRadius: "12px", overflow: "hidden" }} 
            onClick={() => window.open(`/products/view/?id=${info.id}`, "_blank")}
        >
            {/* Image */}
            <img
                src={info.image ? baseURL + info.image : defaultImage}
                alt={info.name}
                className="card-img-top"
                style={{ height: "200px", objectFit: "cover" }}
            />

            <div className="card-body d-flex flex-column justify-content-between">
            {/*  Name, Category, Condition */}
            <div>
                <h5 className="card-title text-truncate" title={info.name}>{info.name}</h5>
                <span className="badge bg-primary me-2" style={{ fontSize: "0.8rem" }}>{info.category}</span>
                <span className="badge bg-secondary" style={{ fontSize: "0.8rem", textTransform: "capitalize" }}>{info.condition}</span>
            </div>

            {/* Prices , Likes , Starts*/}
            <div className="d-flex justify-content-between align-items-center mt-3">
                <div>
                <strong className="text-success" style={{ fontSize: "1.1rem" }}>
                    {info.price} {info.currency_type}
                </strong>
                </div>

                <div className="d-flex align-items-center gap-2" style={{ fontSize: "0.9rem" }}>
                {/* Stars */}
                <div className="text-warning" title={`${info.stars} stars`}>
                    {[...Array(5)].map((_, i) => {
                        return (
                            <i
                            key={i}
                            className={i < Math.round(info.stars) ? "fas fa-star" : "far fa-star"}
                            style={{ color: i < Math.round(info.stars) ? "#f5c518" : "#ddd" }}
                            />
                        );
                    })}

                </div>

                {/* Likes */}
                <div className="text-danger d-flex align-items-center" title={`${info.likes} likes`}>
                    <i className="fas fa-heart me-1"></i>
                    <span>{info.likes}</span>
                </div>
                </div>
            </div>
            </div>
        </div>
    </div>
  );
}

export default Product;
