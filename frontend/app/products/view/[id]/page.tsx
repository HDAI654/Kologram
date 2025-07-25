import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";
import defaultImage from "@/app/DefaultImage";
import ReactMarkdown from "react-markdown";
import baseURL from "@/app/BaseURL";
import MainNavbar from "@/app/component/MainNav";
import "@/public/MainNav.css"


// create metadata
export async function generateMetadata({ params }: { params: { id: string } }) {
  const { id } = params;
  try {
    const res = await fetch(`${baseURL}/prd-api/getPrdByID?id=${id}`, {
      next: { revalidate: 1200 },
    });

    if (!res.ok) throw new Error("Failed to fetch");

    const data = await res.json();
    const product = data.product;

    if (!product) {
      return {
        title: "Product Not Found",
        description: "This product does not exist or has been removed.",
      };
    }

    const imageUrl = product.image ? `${baseURL}${product.image}` : defaultImage;

    return {
      title: `${product.name} | Buy Online at the Best Price`,
      description: `Details, price, and specifications of ${product.name} | Category: ${product.category} | Condition: ${product.condition} | Price: ${product.price} ${product.currency_type}`,
      openGraph: {
        title: product.name,
        description: product.description?.slice(0, 150) || "",
        url: `https://kologram.com/products/view/${product.id}`,
        type: "article",
        images: [
          {
            url: imageUrl,
            alt: product.name,
          },
        ],
      },
      twitter: {
        card: "summary_large_image",
        title: product.name,
        description: product.description?.slice(0, 150) || "",
        images: [imageUrl],
      },
    };
  } catch (error) {
    return {
      title: "Error Fetching Product Data",
      description: "There was an issue retrieving information about this product.",
    };
  }
}

async function getProductData(id: string) {
  const res = await fetch(`${baseURL}/prd-api/getPrdByID?id=${id}`, {
    next: { revalidate: 1200 } // ISR every 20 minutes (1200 seconds)
  });
  
  if (!res.ok) {
    throw new Error('Failed to fetch product data');
  }
  
  return res.json();
}

export async function generateStaticParams() {
  const res = await fetch(`${baseURL}/prd-api/all-prd-ids`, {
    next: { revalidate: 1200 }
  });
  
  if (!res.ok) {
    return [];
  }
  
  const products = await res.json();
  return products.products.map((product: any) => ({
    id: product.id.toString(),
  }));
}

async function Viewprd({ params }: { params: { id: string } }) {
  const { id } = params;
  
  const productData = await getProductData(id);
  console.log(productData);
  
  if (!productData ) {
    return <p style={{ color: "red" }}>Invalid product !!!</p>;
  }
  
  const info = productData.product;
  info.image = info.image ? `${baseURL}${info.image}` : defaultImage;

  return (
    <>
      <MainNavbar />

      <main className="container-fluid" style={{ paddingTop: "calc(var(--navbar-height) + 20px)", paddingBottom: "100px" }}>
        <div className="row rounded-top-5 rounded-bottom-5 bg-contrast">
          <div className="col-lg-6 col-md-12 col-sm-12 p-3">
            <img
              src={info.image}
              className="img-fluid w-100"
              alt={info.name || "product image"}
              style={{ height: "50vh", objectFit: "contain" }}
            />
          </div>

          <div className="col-lg-6 col-md-12 col-sm-12 p-3 text-left">
            <h1 className="text-primary mt-4 text-wrap h2">
              {info.name} 
            </h1>
            <div className="text-warning" title={`${info.stars} stars`}>
                {[...Array(5)].map((_, i) => (
                  <i
                    key={i}
                    className={i < Math.round(info.stars) ? "fas fa-star" : "far fa-star"}
                    style={{ color: i < Math.round(info.stars) ? "#f5c518" : "#ddd" }}
                  />
                ))}
             </div>
            <p className="text-left text-wrap h5 mb-2 text-body">
              category: {info.category}
            </p>

            <h5 className="text-left text-wrap text-dark text-body">
              {info.price} {info.currency_type} 
              <span className="badge bg-body text-contrast rounded-5 text-wrap ms-2 ">
                {info.condition}
              </span>
              <span className="badge bg-warning text-dark rounded-5 text-wrap ms-2">
                Add to Cart
              </span>
            </h5>
            <hr className="text-dark"/>
            <h5 className="text-left text-wrap text-body">About this item :</h5>
            
            <div className="text-left text-wrap border rounded-3 p-2 text-body" style={{maxHeight: "45vh", overflowY: "auto"}}>
              <ReactMarkdown>{info.description}</ReactMarkdown>
            </div>
          </div>
        </div>

      </main>
    </>
  );
}

export default Viewprd;