"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import { useEffect, useState } from "react";
import axios from "axios";
import baseURL from "../BaseURL";
import defaultImage from "../DefaultImage";
import "@/public/myPrd.css";
import { toast } from 'react-toastify';
import getCookie from "../getCookie";
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';
import EditProductModal from "./EditPrdModal";
import '@/public/entry-styles.css'

const MySwal = withReactContent(Swal);

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function MyProductPage() {
  const [myPrd, setMyPrd] = useState([]);
  const [errorSTS, seterrorSTS] = useState(false);
  const [isSmallScreen, setSmallScreen] = useState(0);
  const [isDelLoad, setDelLoad] = useState(false);

  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [modalKey, setModalKey] = useState(0);

  const get_prds = async () => {
    try {
        const res = await axios.get(`/prd-api/get_products?by_user=1`);
        const prds = res.data.products
        if (prds === false) {
            seterrorSTS(true);
            return; 
        } else {
          setMyPrd(prds)
          return; 
        }
    } catch (err : any) {
        seterrorSTS(true);
        return; 
    }
  }

  useEffect(() => {
    get_prds();

    handleResize();
    window.addEventListener("resize", handleResize)
  }, []);

  const handle_prd_click = (id:number) => {
    if (!id) {return;}
    try {
      window.open(`/products/view/?id=${id}`, '_blank');
    } catch (err : any) {
      toast.error("Something went wrong. Try again.");
      return;
    }
  };

  const handleEditClick = async (id: number) => {
    try {
      const res = await axios.get(`/prd-api/get_products?id=${id}`);
      const data = res.data.products;

      if (!data || !Array.isArray(data) || data.length === 0) {
        toast.error("Product not found.");
        return;
      }

      setSelectedProduct(data[0]);
      setShowEditModal(true);
    } catch (err) {
      toast.error("Failed to load product.");
    }
  };

  const setEditToServer = async () => {
    try{
      const formData = new FormData();
      formData.append("id", selectedProduct.id.toString());
      formData.append("name", selectedProduct.name);
      formData.append("discription", selectedProduct.discription || selectedProduct.description || "");
      formData.append("price", selectedProduct.price.toString());
      formData.append("currency_type", selectedProduct.currency_type);
      formData.append("condition", selectedProduct.condition);

      if (selectedProduct.image) {
        formData.append("image", selectedProduct.image);
      }

      const csrfToken = getCookie("csrftoken");
      const res = await axios.post("/prd-api/editPrd/", formData, {
        headers: {
          "X-CSRFToken": csrfToken,
        },
      });
      if (res.data.result === true) {
        toast.info("Your product edited successful");
      }
    }catch (err: any) {
      console.log(err)
      if (err.response) {
        if (err.response.status === 400) {
          toast.error("Invalid data !");
        } else if (err.response.status === 401) {
          toast.error("Login required to edit a product!");
        } else if (err.response.status === 404) {
          toast.error("Product not found or permission denied.");
        } else {
          toast.error("Something went wrong. Try again.");
        }
      } else {
        toast.error("Network error or server not reachable.");
      }
    } finally {
      setModalKey(prev => prev + 1);
      get_prds();
    }
  };

  const handleDelClick = async (id:number) => {
    try{
      const result = await MySwal.fire({
        title: 'Are you sure?',
        text: "This product will be deleted!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel'
      });

      if (result.isConfirmed) {
        deleteProduct(id);
      }   
    }catch (err: any) {
      toast.error("Network error or server not reachable.");
    }
  };

  const deleteProduct = async (id:number) => {    
    try{
      setDelLoad(true);

      const csrfToken = getCookie("csrftoken");
      const res = await axios.post("/prd-api/delPrd/", {"id":id}, {
        headers: {
          "X-CSRFToken": csrfToken,
          "Content-Type": "application/json"
        },
      });

      if (res.data.result === true) {
        toast.info("Your product Deleted successful");
        setMyPrd(prevPrds => prevPrds.filter(prd => prd.id !== id));
      }
    }catch (err: any) {
      if (err.response) {
        if (err.response.status === 400) {
          toast.error("Invalid data ! couldn't find your product");
        } else if (err.response.status === 404) {
          toast.error("This product is not exist !!");
        } else {
          toast.error("Something went wrong. Try again.");
        }
      } else {
        toast.error("Network error or server not reachable.");
      }
    } finally {
      setDelLoad(false);
    }
  };

  const handleResize = () => {
    let width = window.innerWidth
    if (width < 320) {
      setSmallScreen(2);
      return;
    }else if (width < 560) {
      setSmallScreen(1);
      return;
    }else {
      setSmallScreen(0);
      return;
    }
  };

  const modalClose = () => {
    setShowEditModal(false);
    setModalKey(prev => prev + 1);
  };

  const chunkedProducts = [];
  for (let i = 0; i < myPrd.length; i += 2) {
    chunkedProducts.push(myPrd.slice(i, i + 2));
  }
  if (errorSTS === true) return (<h1 className="mt-5 text-light text-center">Error in found your products</h1>)

  return (
    <>

      <EditProductModal
        key={modalKey}
        show={showEditModal}
        onClose={modalClose}
        product={selectedProduct}
        setProduct={setSelectedProduct}
        onSave={() => {
          setShowEditModal(false);
          setEditToServer();
        }}
      />

      <div className="container">

        {chunkedProducts.map((group, rowIndex) => (
          <div className="row w-100" key={rowIndex}>
            {group.map((v, i) => (
              <div className={`col-lg-6 col-md-12 col-sm-12 py-2 d-flex align-items-center rounded-5 mt-3 bg-light ${isSmallScreen === 2 && "justify-content-center"} scale-in`} id="myprd_div" key={i}>
                { isSmallScreen!==2 && <img
                  src={v.image === null ? defaultImage : baseURL + v.image}
                  className="img-fluid ml-1"
                  alt={v.name || "product image"}
                  style={{ height: "10vh", objectFit: "contain" }}
                /> }

                <h5 className={`card-title text-primary text-wrap ml-3 ${isSmallScreen === 2 && 'text-center justify-content-center'}`}>
                  {v.name}
                  {isSmallScreen > 0 && <br />}
                  <span className="badge bg-success text-light rounded-5 text-wrap ms-2" style={{cursor:"pointer"}} onClick={() => handleEditClick(v.id)}>
                    Show/Edit
                  </span>
                  
                  {isDelLoad ? <span className="spinner-border spinner-border-sm text-light" role="status" aria-hidden="true"></span> : <span className="badge bg-danger text-light rounded-5 text-wrap ms-2" style={{cursor:"pointer"}} onClick={() => handleDelClick(v.id)}>Delete</span> }

                  <span className="badge bg-primary text-light rounded-5 text-wrap ms-2" style={{cursor:"pointer"}} onClick={() => handle_prd_click(v.id)}>
                    Open
                  </span>
                </h5>
    
              </div>
            ))}
          </div>
        ))}

      </div>
    </>
  );
}

export default MyProductPage;
