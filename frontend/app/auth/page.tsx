"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import Login_component from "./login";
import Reg_component from "./reg";
import { useState } from "react";
import Head from "next/head";

export default function login() {
  const [log_reg, set_log_reg] = useState("0")
  return (
    <>
      <Head>
        <title>Login / Register – Kologram</title>
        <meta name="description" content="Access your Kologram account or create a new one to explore and purchase premium digital products like software, ebooks, templates, and more." />
        <meta name="keywords" content="login, register, sign up, account, Kologram, digital products, software, ebook, template, marketplace" />
        <meta name="author" content="Kologram Team" />
        
        {/* Open Graph Meta Tags */}
        <meta property="og:title" content="Login / Register – Kologram" />
        <meta property="og:description" content="Log in or create an account on Kologram to access top-tier digital products." />
        <meta property="og:type" content="website" />
        <meta property="og:url" content="https://kologram.com/login" />
        <meta property="og:image" content="https://kologram.com/images/og-login-preview.png" />

        {/* Twitter Meta Tags */}
        <meta name="twitter:title" content="Login / Register – Kologram" />
        <meta name="twitter:description" content="Join Kologram to access the best collection of digital products online." />
        <meta name="twitter:image" content="https://kologram.com/images/og-login-preview.png" />
        <meta name="twitter:card" content="summary_large_image" />
      </Head>

      {log_reg === "0" && <Login_component setPage={set_log_reg} />}
      {log_reg === "1" && <Reg_component setPage={set_log_reg} />}
    </>
     
  );
}
