"use client";

import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay, Pagination, Navigation } from "swiper/modules";
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";
import baseURL from "../BaseURL";
import Link from "next/link";

interface Banner {
  image: string;
}

export default function BannerSlider({ banners }: { banners: Banner[] }) {
  return (
    <div className="container position-relative">
      <Swiper
        modules={[Autoplay, Pagination, Navigation]}
        autoplay={{ delay: 3000 }}
        pagination={{ clickable: true }}
        navigation={true}
        loop={true}
        spaceBetween={20}
        slidesPerView={1}
        className="rounded-4 shadow"
        style={{ height: "300px" }}
      >
        {banners.map((banner:any, index) => (
          <SwiperSlide key={index}>
            <Link href={banner.link || "#"} className="text-decoration-none">
              <div
                className="position-relative d-flex align-items-center justify-content-center text-white overflow-hidden rounded-4"
                style={{
                  backgroundImage: `url(${baseURL + banner.image})`,
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                  height: "100%",
                }}
              >
                

                {banner.title && banner.text && <>
                <div
                  className="position-absolute w-100 h-100 top-0 start-0"
                  style={{
                    background: "rgba(0, 0, 0, 0.4)",
                  }}
                ></div>
                
                <div className="position-relative text-center px-4">
                  <h3 className="fw-bold text-uppercase mb-2" style={{ fontSize: "1.5rem" }}>
                    {banner.title || "Title here..."}
                  </h3>
                  <p className="mb-3">
                    {banner.text || "Text here..."}
                  </p>
                </div></>}
              </div>
            </Link>
          </SwiperSlide>

        ))}
      </Swiper>
    </div>
  );
}
