"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import React from "react";


function Prd({name, description}:{name : string, description : string}) {  
  return (
    <div className="container-fluid bg-dark w-100">
        <h1>{name}</h1>
        <p>{description}</p>
    </div>
  );
}

export default Prd;
