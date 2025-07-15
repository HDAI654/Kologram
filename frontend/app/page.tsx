"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import { useEffect, useState, useRef } from "react";
import axios from "axios";
import baseURL from "./BaseURL";
import { useRouter } from "next/navigation";
import Loading_component from "./component/Loading";
import HomeNavbar from "./component/homeNav";
import { Swiper, SwiperSlide } from "swiper/react";
import { Autoplay, Pagination, Navigation } from "swiper/modules";
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";
import PrdSeachPage from "./component/PrdSearchPage";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

export default function Home() {
  const router = useRouter();
  const [load, setLoad] = useState(false);
  const [error, setError] = useState("");
  const [isLogin, setLogin] = useState(false);
  const [screenMode, setscreenMode] = useState("lg");
  const username = useRef("Guest");
  const [searchValue, setSearchValue] = useState("");

  useEffect(() => {
    document.title = "Kologram - Home";

    handleResize();
    window.addEventListener("resize", handleResize)

    axios.get("/auth/get_auth/")
    .then((res) => {
      if (res.data.auth === false) {
        setLogin(false);
      } else {
        username.current = res.data.username;
        setLoad(true);
        setLogin(true);
      }
    })
    .catch((err) => setLoad(false));
    
  }, []);

  const handleResize = () => {
    let width = window.innerWidth
    if (width < 400) {
      setscreenMode("lt");
      return;
    }else if (width < 530) {
      setscreenMode("sm");
      return;
    }else if (width < 940) {
      setscreenMode("md");
      return;
    }else {
      setscreenMode("lg");
      return;
    }
  };


  if (load === false) {
    return (
      <Loading_component />
    );
  }

  return (
    <>
      {/* Navbars */}
      <HomeNavbar screenMode={screenMode} isLogin={isLogin} username={username.current} setSearchValue={setSearchValue} />

      {/* Main Content */}
      <div style={{ marginTop: "90px", marginBottom: "90px" }}>
        
        

        { searchValue === "" ? (
          // Slider to show the best products and advertisements
          <div className="container position-relative">
            <Swiper
              modules={[Autoplay, Pagination, Navigation]}
              autoplay={{ delay: 3000 }}
              pagination={{ clickable: true }}
              navigation={screenMode !== "sm" ? true : false}
              loop={true}
              spaceBetween={20}
              slidesPerView={1}
              className="rounded-4 shadow"
            >

              <SwiperSlide>
                <img
                  src="https://picsum.photos/id/1015/800/400"
                  alt="Slide 1"
                  className="img-fluid w-100 rounded-4"
                />
              </SwiperSlide>
              <SwiperSlide>
                <img
                  src="https://picsum.photos/id/1016/800/400"
                  alt="Slide 2"
                  className="img-fluid w-100 rounded-4"
                />
              </SwiperSlide>
              <SwiperSlide>
                <img
                  src="https://picsum.photos/id/1018/800/400"
                  alt="Slide 3"
                  className="img-fluid w-100 rounded-4"
                />
              </SwiperSlide>

            </Swiper>
          </div>
        ) : <PrdSeachPage searchValue={searchValue} setSearchValue={setSearchValue} />}
        

        {/* Footer */}
        <hr className="w-100 mt-5" />
        <div className="container">
          <footer className="py-5">
            <div className="row">
              {[1, 2, 3].map((_, index) => (
                <div className="col-6 col-md-2 mb-3" key={index}>
                  <h5>Section</h5>
                  <ul className="nav flex-column">
                    <li className="nav-item mb-2">
                      <a href="#" className="nav-link p-0 text-body-secondary">Home</a>
                    </li>
                    <li className="nav-item mb-2">
                      <a href="#" className="nav-link p-0 text-body-secondary">Features</a>
                    </li>
                    <li className="nav-item mb-2">
                      <a href="#" className="nav-link p-0 text-body-secondary">Pricing</a>
                    </li>
                    <li className="nav-item mb-2">
                      <a href="#" className="nav-link p-0 text-body-secondary">FAQs</a>
                    </li>
                    <li className="nav-item mb-2">
                      <a href="#" className="nav-link p-0 text-body-secondary">About</a>
                    </li>
                  </ul>
                </div>
              ))}

              {/* Collect Emails form */}
              <div className="col-md-5 offset-md-1 mb-3">
                <form>
                  <h5>Subscribe to our newsletter</h5>
                  <p>Monthly digest of what's new and exciting from us.</p>
                  <div className="d-flex flex-column flex-sm-row w-100">
                    <label htmlFor="newsletter1" className="visually-hidden">Email address</label>
                    <input
                      id="newsletter1"
                      type="email"
                      className="form-control"
                      placeholder="Email address"
                    />
                    <button className="btn btn-primary " type="button">
                      Subscribe
                    </button>
                  </div>
                </form>
              </div>
            </div>
            
            {/* Contact Information */}
            <div className="container py-4 border-top">
              <div className="row align-items-center">
                <div className="col-md-6 text-center text-md-start mb-3 mb-md-0">
                  <p className="mb-0">© 2025 Company, Inc. All rights reserved.</p>
                </div>

                <div className="col-md-6">
                  <div className="d-flex justify-content-center justify-content-md-end align-items-center gap-3 flex-wrap">

                    {/* Telegram */}
                    <a className="h5" href="https://t.me/yourtelegram" target="_blank" rel="noopener noreferrer" aria-label="Telegram">
                      <i className="fab fa-telegram fa-lg"></i>
                    </a>

                    {/* Facebook */}
                    <a className="h5" href="https://facebook.com/yourpage" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
                      <i className="fab fa-facebook fa-lg"></i>
                    </a>

                    {/* GitHub */}
                    <a className="h5" href="https://github.com/HDAI654" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
                      <i className="fab fa-github fa-lg"></i>
                    </a>

                    {/* Gmail */}
                    <a className="h5 d-flex align-items-center gap-1" href="mailto:hdai.code@gmail.com" aria-label="Gmail">
                      <i className="fas fa-envelope fa-lg"></i>
                      <span className="d-none d-sm-inline">hdai.code@gmail.com</span>
                    </a>

                  </div>
                </div>
              </div>
            </div>

          </footer>
        </div>
      </div>
    </>
  );
}
