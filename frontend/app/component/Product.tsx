import React from "react";
import Link from "next/link";
import baseURL from "@/app/BaseURL";
import defaultImage from "@/app/DefaultImage";
import Image from "next/image";

type ProductInfo = {
  id: number;
  name: string;
  image?: string;
  category: string;
  condition: string;
  price: number;
  currency_type: string;
  stars: number;
  likes: number;
};

function Product({ info }: { info: ProductInfo }) {
  return (
    <div className="col-12 col-md-6 col-lg-4 mb-4 d-flex">
      <Link
        href={`/products/view/${info.id}`}
        className="card shadow-sm combo-animate flex-fill"
        style={{ 
          borderRadius: "12px", 
          overflow: "hidden", 
          display: "flex", 
          flexDirection: "column",
          textDecoration: "none",
          color: "inherit"
        }}
        title={info.name}
      >
        <div style={{ position: "relative", width: "100%", aspectRatio: "16/9" }}>
          <Image
            src={info.image ? baseURL + info.image : defaultImage}
            alt={`${info.name} in ${info.category} category`}
            fill
            style={{ objectFit: "cover", borderRadius: "12px 12px 0 0" }}
            priority={false} 
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        </div>
        <div className="card-body d-flex flex-column justify-content-between flex-grow-1">
          <div>
            <h2 className="card-title text-truncate h5">{info.name}</h2>
            <span className="badge bg-primary me-2" style={{ fontSize: "0.8rem" }}>
              {info.category}
            </span>
            <span
              className="badge bg-secondary"
              style={{ fontSize: "0.8rem", textTransform: "capitalize" }}
            >
              {info.condition}
            </span>
          </div>

          <div className="d-flex justify-content-between align-items-center mt-3">
            <strong className="text-success" style={{ fontSize: "1.1rem" }}>
              {info.price} {info.currency_type}
            </strong>

            <div className="d-flex align-items-center gap-2" style={{ fontSize: "0.9rem" }}>
              <div className="text-warning" title={`${info.stars} stars`}>
                {[...Array(5)].map((_, i) => (
                  <i
                    key={i}
                    className={i < Math.round(info.stars) ? "fas fa-star" : "far fa-star"}
                    style={{ color: i < Math.round(info.stars) ? "#f5c518" : "#ddd" }}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </Link>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Product",
            "name": info.name,
            "image": baseURL + info.image,
            "description": `Condition: ${info.condition}`,
            "brand": {
              "@type": "Brand",
              "name": info.category
            },
            "offers": {
              "@type": "Offer",
              "priceCurrency": info.currency_type,
              "price": info.price,
              "availability": "https://schema.org/InStock"
            }
          })
        }}
      />
    </div>
  );
}

export default Product;
