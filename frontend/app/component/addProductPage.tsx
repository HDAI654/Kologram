"use client";
import "bootstrap/dist/css/bootstrap.min.css";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import axios from "axios";
import baseURL from "../BaseURL";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import getCookie from "../getCookie";

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

function AddProductPage({hidden=true}:{hidden:boolean}) {
  const [info_markdown, set_info_markdown] = useState("0")
  const [info_markdown_mode, set_info_markdown_mode] = useState("0")
  const [discriptionText, setDiscriptionText] = useState("")
  const [submitLoad, setSubmitLoad] = useState(false)
  const currency_choices = [
        ['USD', 'US Dollar'],
        ['IRR', 'Iranian Rial'],
        ['EUR', 'Euro'],
        ['GBP', 'British Pound'],
        ['JPY', 'Japanese Yen'],
        ['CHF', 'Swiss Franc'],
        ['CAD', 'Canadian Dollar'],
        ['AUD', 'Australian Dollar'],    
        ['NZD', 'New Zealand Dollar'],
        ['CNY', 'Chinese Yuan'],
        ['INR', 'Indian Rupee'],
        ['RUB', 'Russian Ruble'],
        ['BRL', 'Brazilian Real'],
        ['ZAR', 'South African Rand'],
        ['KRW', 'South Korean Won'],
        ['MXN', 'Mexican Peso'],
        ['SGD', 'Singapore Dollar'],
        ['HKD', 'Hong Kong Dollar'],
        ['SEK', 'Swedish Krona'],
        ['NOK', 'Norwegian Krone'],
        ['TRY', 'Turkish Lira'],
    ]
  
  useEffect(() => {
    handleResize();
    window.addEventListener("resize", handleResize)
  }, []);

  const handleResize = () => {
    let width = window.innerWidth
    if (width < 768) {
      set_info_markdown_mode("0");
    } else {
      set_info_markdown_mode("1");
    }
  }

  const handleShowMarkdownClick = () => {
    let new_value = info_markdown == "0" ? "1" : "0"
    set_info_markdown(new_value)
  }

  const handleAddPrd = async (e: React.FormEvent<HTMLFormElement>) => {
    try{
      setSubmitLoad(true)
      e.preventDefault(); // Prevent the default form submission behavior
      const form = e.currentTarget;
      const formData = new FormData(form);
      const data = {
        name: formData.get("name"),
        discription: formData.get("discription"),
        price: formData.get("price"),
        currency_type: formData.get("currency_type"),
        image: formData.get("image"),
      };

      console.log(data)
      const csrfToken = getCookie("csrftoken");
      const res = await axios.post("/prd-api/addPrd/", data, {
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrfToken},
      });

      if (res.data.result === true) {
        toast.info("Your product created successful");
      } else {
        toast.error("Something went wrong. Try again.");
      }
    } catch (err : any) {
      if (err.response && err.response.status === 422) {
        toast.error("Invalid data !");
      }  else {
        toast.error("Something went wrong. Try again.");
      }
    } finally {
      setSubmitLoad(false)
    }

  }

  return (
    <>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
      />
      <div className="container" hidden={hidden}>
          <div className="row">
            <div className="col-12">
              <form className="form-group" onSubmit={handleAddPrd}>
                <label htmlFor="name" className="form-label text-light mt-4 text-wrap" > Name </label>
                <input type="text" className="form-control mb-3 text-wrap" id="name" placeholder="Enter the name of your product" name="name" required />

                <label htmlFor="discription" className="form-label text-light mt-4 text-wrap" >
                  Discription  {info_markdown_mode === "0" && <span className="badge bg-light text-dark rounded-5" onClick={handleShowMarkdownClick}>{info_markdown === "0" ? 'show markdown' : 'show text'}</span>}
                </label>
                {info_markdown_mode === "0" && info_markdown === "0" && <textarea className="form-control mb-3 text-wrap" id="discription" placeholder="Enter discription of your product" style={{minHeight:"400px"}} name="discription" value={discriptionText} onChange={((v) => {setDiscriptionText(v.target.value)})} required />}
                {info_markdown_mode === "0" && info_markdown === "1" && <div className="bg-light rounded-3 p-1" style={{height:"400px"}}><ReactMarkdown>{discriptionText}</ReactMarkdown></div>}
                {info_markdown_mode === "1" && <div className="d-flex"><textarea className="form-control mb-3 text-wrap w-50" id="discription" placeholder="Enter discription of your product" style={{minHeight:"400px"}} name="discription" value={discriptionText} onChange={((v) => {setDiscriptionText(v.target.value)})} required /><div className="bg-light rounded-3 p-1 w-50" style={{height:"400px"}}><ReactMarkdown>{discriptionText}</ReactMarkdown></div></div>}


                <label htmlFor="price" className="form-label text-light mt-4 text-wrap" > Price </label>
                <input type="number" className="form-control mb-3 text-wrap" id="price" placeholder="Enter the price of your product" name="price" required />

                <label htmlFor="currency_type" className="form-label text-light mt-4 text-wrap" > Currency Type </label>
                <select className="form-select" id="currency_type" name="currency_type">
                  {currency_choices.map((value, index) => (
                    <option value={value[0]} key={index}>{value[1]}</option>
                  ))}
                </select>
                
                <label htmlFor="image" className="form-label text-light mt-4 text-wrap" > Image </label>
                <input type="file" className="form-control mb-3 text-wrap" id="image" name="image" />

                { submitLoad === false ? <button type="submit" className="btn btn-success mb-5 w-100">Add</button> : <button type="submit" className="btn btn-success mb-5 w-100" disabled>
                  <span
                    className="spinner-border spinner-border-sm text-light"
                    role="status"
                    aria-hidden="true"
                  ></span></button> }
              </form>
            </div>
          </div>
      </div>
    </>
  );
}

export default AddProductPage;