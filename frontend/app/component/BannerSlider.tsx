"use client";

import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay, Pagination, Navigation } from "swiper/modules";
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";
import baseURL from "../BaseURL";

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
        {banners.map((banner, index) => (
          <SwiperSlide key={index}>
            <img
              src={baseURL + banner.image}
              alt={`Slide ${index + 1}`}
              className="img-fluid w-100 rounded-4"
            />
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
}
