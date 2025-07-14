"use client";

import React, { useState } from "react";
import baseURL from "../BaseURL";
import defaultImage from "../DefaultImage";
import currencyChoices, {category_choices} from "../currency_choices"; 
import '@/public/entry-styles.css'

interface EditProductModalProps {
  show: boolean;
  onClose: () => void;
  product: any;
  setProduct: (p: any) => void;
  onSave: () => void;
}

const EditProductModal: React.FC<EditProductModalProps> = ({
  show,
  onClose,
  product,
  setProduct,
  onSave,
}) => {
    const [previewImage, setPreviewImage] = useState<string | null>(null);

    const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
          const file = e.target.files[0];
          setProduct({ ...product, image: file });

          const reader = new FileReader();
          reader.onloadend = () => {
              setPreviewImage(reader.result as string);
          };
          reader.readAsDataURL(file);
      }
    };


  if (!product) return null;

  return (
    <div
      className={`modal fade show ${show ? "d-block" : "d-none"}`}
      tabIndex={-1}
      style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
    >
      <div className="modal-dialog modal-lg modal-dialog-centered">
        <div className="modal-content">

          <div className="modal-header">
            <h5 className="modal-title">Edit Product</h5>
            <button type="button" className="btn-close" onClick={() => {
              setPreviewImage(null);
              onClose();
            }}></button>
          </div>

          <div className="modal-body slide-up">
            <div className="mb-3">
              <label className="form-label">Name</label>
              <input
                type="text"
                className="form-control"
                value={product.name}
                onChange={(e) =>
                  setProduct({ ...product, name: e.target.value })
                }
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Description</label>
              <textarea
                className="form-control"
                rows={3}
                value={product.description}
                onChange={(e) =>
                  setProduct({ ...product, description: e.target.value })
                }
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Price</label>
              <input
                type="number"
                className="form-control"
                value={product.price}
                onChange={(e) =>
                  setProduct({ ...product, price: e.target.value })
                }
              />
            </div>

            <div className="mb-3">
              <label className="form-label">Currency</label>
              <select
                className="form-select"
                value={product.currency_type}
                onChange={(e) =>
                  setProduct({ ...product, currency_type: e.target.value })
                }
              >
                {currencyChoices.map((value, index) => (
                    <option value={value[0]} key={index}>{value[1]}</option>
                ))}
              </select>
            </div>

            <div className="mb-3">
              <label className="form-label">Product Condition</label>
              <select
                className="form-select"
                value={product.condition}
                onChange={(e) =>
                  setProduct({ ...product, condition: e.target.value })
                }
              >
                <option value={"New"}>New</option>
                <option value={"Used"}>Used</option>
              </select>
            </div>

            <div className="mb-3">
              <label className="form-label">Category</label>
              <select
                className="form-select"
                value={product.category}
                onChange={(e) =>
                  setProduct({ ...product, category: e.target.value })
                }
              >
                {category_choices.map((value, index) => (
                    <option value={value[0]} key={index}>{value[1]}</option>
                ))}
              </select>
            </div>
            
            <div className="mb-3">
                <input
                    type="file"
                    accept="image/*"
                    className="form-control mt-2"
                    onChange={handleImageChange}
                />
            </div>

            <div className="text-center mb-3">
                <img
                    src={previewImage || (product.image ? baseURL + product.image : defaultImage)}
                    alt="Product"
                    className="img-fluid"
                    style={{ maxHeight: "200px" }}
                />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={() => {
              setPreviewImage(null);
              onClose();
            }}>
              Cancel
            </button>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => {
                setPreviewImage(null);
                onSave();
              }}
            >
              Save
            </button>
          </div>

        </div>
      </div>
    </div>
  );
};

export default EditProductModal;
