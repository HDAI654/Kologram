"use client";
import "bootstrap/dist/css/bootstrap.min.css";

function Loading_component() {
  return (
    <div className="container-fluid vh-100 bg-dark d-flex justify-content-center align-items-center">
      <div className="d-flex align-items-center gap-3">
        <div className="spinner-border text-light" style={{ width: "3rem", height: "3rem" }} role="status" />
        <h1 className="text-light m-0">Loading ...</h1>
      </div>
    </div>

  );
}

export default Loading_component;
