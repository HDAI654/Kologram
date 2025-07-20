import "bootstrap/dist/css/bootstrap.min.css";
import axios from "axios";
import baseURL from "../BaseURL";
import CATEGORIES from "../categories";
import Link from "next/link";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

export default function Sidebar({username="Guest"}:{username:string}) {

  return (
    <div className="offcanvas offcanvas-end rounded-end-3" id="sidebarMenu">
      {/* Header with user icon */}
      <div className="offcanvas-header flex-column align-items-start w-100 border-bottom">
        <div className="d-flex align-items-center w-100"> 
          <i className="fas fa-user fa-lg me-2"></i>
          <span className="fs-5">{username}</span>
          <button
              type="button"
              className="btn-close"
              data-bs-dismiss="offcanvas"
              aria-label="Close"
            ></button>
        </div>
      </div>

      {/* Body */}
      <div className="offcanvas-body p-0">

        {/* All Categories */}
        <div className="border-bottom w-100 mx-0">
          <button
            className="btn bg-transparent border-0 mt-2 w-100 text-start"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#CategoryCollapse"
            aria-expanded="true"
            aria-controls="CategoryCollapse"
          >
            <p className="h4">Categories <i className="fas fa-chevron-down"></i></p>
          </button>

          <div className="collapse show border rounded p-2 m-2 mb-0" id="CategoryCollapse">
            <div style={{maxHeight: "70vh", overflowY: "auto"}}>
              {CATEGORIES.map((category:any, index:number) => (
                <div key={index}>
                  <Link 
                  href={`/category/${category[0]}`} 
                  className="text-decoration-none" 
                  title={`Go to Category ${category[1]}`} 
                  aria-label={`Go to Category ${category[1]}`}>
                    <h4 className="mt-3">{category[1]}</h4>
                  </Link>
                </div>
              ))}
            </div>
          </div>
        </div>
        

        <ul className="list-unstyled w-100 p-3">
          <li className="mt-3"><a href="/" className="nav-link"><i className="fas fa-home me-2" />Home</a></li>
          <li className="mt-3"><a href="/panel" className="nav-link"><i className="fas fa-user me-2" />Panel</a></li>
          <li className="mt-3"><a href="/cart" className="nav-link"><i className="fas fa-shopping-cart me-2" />My Cart</a></li>
        </ul>

      </div>
    </div>
  );
}
