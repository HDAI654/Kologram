import baseURL from "./BaseURL";
import MainNavbar from "./component/MainNav";
import BannerSlider from "./component/BannerSlider";
import type { Metadata } from "next";
import TopPrds from "./component/TopPrds";


// Metadata
export const metadata: Metadata = {
  title: "Kologram | Online Shopping for Quality Products",
  description: "Discover the best deals and premium products at Kologram. Shop electronics, fashion, home goods, and more with fast delivery and secure checkout.",
  keywords: [
    "Kologram",
    "online shopping",
    "buy products online",
    "best ecommerce store",
    "electronics",
    "fashion",
    "home essentials",
    "free delivery",
    "quality products",
  ],
  openGraph: {
    title: "Kologram | Shop Smart, Live Better",
    description: "Kologram is your go-to destination for top-notch products and unbeatable prices. Start shopping today.",
    url: "https://kologram.com",
    siteName: "Kologram",
    images: [
      {
        url: "https://kologram.com/og-image.jpg",
        width: 1200,
        height: 630,
        alt: "Kologram Online Store",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Kologram | Premium Online Store",
    description: "Shop quality products at Kologram with fast delivery and secure checkout.",
    creator: "@kologram",
    images: ["https://kologram.com/og-image.jpg"],
  },
};


// Fetch banners from the API
async function getBanners() {
  try {
    const res = await fetch(baseURL + "/ad/get-banners", {
      next: {
        revalidate: 10, // ISR every 12 hours
      },
    });

    if (!res.ok) {
      return [];
    }

    const data = await res.json();

    if (!data || data.error || !Array.isArray(data.banners)) {
      return [];
    }

    return data.banners;
  } catch (error) {
    return [];
  }
}

// HomePage component
export default async function HomePage() {
  const banners = await getBanners();

  return (
    <>
      {/* Top Navbar */}
      <MainNavbar />

      {/* Main Content */}
      <main style={{ paddingTop: "calc(var(--navbar-height) + 20px)", paddingBottom: '100px'  }}>


        {/* Example Rendering */}
        {banners.length > 0 && <BannerSlider banners={banners} />}

        {/* Top Products */}
        <TopPrds />

        {/* Footer */}
        <hr className="w-100" />
        <div className="container">
          <footer className="py-5">
            <div className="row">
              <div className="col-6 col-md-2 mb-3">
                  <h5>Section</h5>
                  <ul className="nav flex-column">
                    <li className="nav-item mb-2">
                      <a href="/" className="nav-link p-0 text-body-secondary">Home</a>
                    </li>
                    <li className="nav-item mb-2">
                      <a href="/reg_banner" className="nav-link p-0 text-body-secondary">Register banner</a>
                    </li>
                    <li className="nav-item mb-2">
                      <a href="/rules" className="nav-link p-0 text-body-secondary">Site Rules</a>
                    </li>
                    <li className="nav-item mb-2">
                      <a href="/faqs" className="nav-link p-0 text-body-secondary">FAQs</a>
                    </li>
                    <li className="nav-item mb-2">
                      <a href="/about" className="nav-link p-0 text-body-secondary">About</a>
                    </li>
                  </ul>
                </div>

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
      </main>
    </>
  );
}
