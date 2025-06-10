import "bootstrap/dist/css/bootstrap.min.css";
import type { Metadata } from "next";
import Products from "./products";

export const metadata: Metadata = {
  title: "Kologram - Products",
  description: "The page of products",
};

export default function products_page() {
  return (
    <>
      <Products />
    </>
     
  );
}
