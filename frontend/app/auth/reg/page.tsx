import "bootstrap/dist/css/bootstrap.min.css";
import type { Metadata } from "next";
import Reg_component from "./reg";

export const metadata: Metadata = {
  title: "Kologram - Register",
  description: "Create a Kologram account",
};

export default function reg() {
  return (
    <>
      <Reg_component />
    </>
  );
}
