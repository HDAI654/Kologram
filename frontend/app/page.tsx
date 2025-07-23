import baseURL from "./BaseURL";
import MainNavbar from "./component/MainNav";
import BannerSlider from "./component/BannerSlider";
import type { Metadata } from "next";
import TopPrds from "./component/TopPrds";
import CategorySlider from "./component/CategorySlider";
import Footer from "./component/footer";
import CountdownOffer from "./component/CountdownOffer";


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
        revalidate: 43200, // ISR every 12 hours
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
        {/* The Site Name */}
        <h1 className="text-center display-1 visually-hidden mb-5">Kologram</h1>


        {/* Example Rendering */}
        {banners.length > 0 && <BannerSlider banners={banners} />}

        <CountdownOffer />

        {/* Category Slider */}
        <CategorySlider />

        {/* Top Products */}
        <TopPrds />

        {/* Footer */}
        <Footer />
      </main>
    </>
  );
}
