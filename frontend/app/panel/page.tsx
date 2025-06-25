import "bootstrap/dist/css/bootstrap.min.css";
import type { Metadata } from "next";
import Panel from "./panel";

export const metadata: Metadata = {
  title: "Kologram - Panel",
  description: "page of user panel",
};

export default function products_page() {
  return (
    <Panel />  
  );
}
