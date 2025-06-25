"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import Login_component from "./login";
import Reg_component from "./reg";
import { useState } from "react";

export default function login() {
  const [log_reg, set_log_reg] = useState("0")
  return (
    <>
      {log_reg === "0" && <Login_component setPage={set_log_reg} />}
      {log_reg === "1" && <Reg_component setPage={set_log_reg} />}
    </>
     
  );
}
