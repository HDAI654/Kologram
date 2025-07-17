export default function Loading() {
  return (
   <div className="container-fluid vh-100 d-flex justify-content-center align-items-center">
      <div className="d-flex align-items-center gap-3">
        <div className="spinner-border" style={{ width: "3rem", height: "3rem" }} role="status" />
        <h1 className="text-wrap m-0">Loading ...</h1>
      </div>
    </div>
  );
}