import "bootstrap/dist/css/bootstrap.min.css";
import type { Metadata } from "next";
import Login_component from "./login";

export const metadata: Metadata = {
  title: "Kologram - Login",
  description: "Login to your Kologram account",
};

export default function login() {
  return (
    <>
      <Login_component />
    </>
     
  );
}
