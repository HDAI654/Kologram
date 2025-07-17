'use client';

import React, { useEffect, useState } from 'react';
import MainNavbar from '@/app/component/MainNav';
import Product from '@/app/component/Product';
import NoPrdFound from '@/app/component/NoPrdFound';
import { useParams, useSearchParams } from 'next/navigation';
import baseURL from '@/app/BaseURL';
import axios from 'axios';
import Loading_component from '@/app/component/Loading';

axios.defaults.baseURL = baseURL;
axios.defaults.withCredentials = true;

export default function SearchPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const [products, setProducts] = useState<any[]>([]);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);

  // Extract page, category, and text from the URL
  const page = parseInt(searchParams.get("page") || '1');
  const slug = params?.slug as string[] || [];
  const category = slug[0] || 'all';
  const text = slug[1] || '';

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      try {
        const res = await axios.get(`/prd-api/search-prd/`, {
          params: {
            search_text: text,
            ...(category !== "all" && { category }),
            page: page - 1
          }
        });

        const data = res.data;
        setProducts(data.products || []);
        setTotalPages(data.totalPages || 0);
      } catch (err) {
        console.error("Search error", err);
        setProducts([]);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, [category, text, page]);

  if (loading) {
    return <Loading_component />;
  }

  return (
    <>
      <MainNavbar />

      <main style={{ padding: '2rem', paddingTop: '100px', paddingBottom: '100px' }}>
        <h1 className="display-6 text-center mb-4">
          Results for "<strong>{text}</strong>" in <strong>{category}</strong>
        </h1>

        {products.length === 0 ? (
          <NoPrdFound />
        ) : (
          <>
            <div className="row">
              {products.map((product) => (
                <Product key={product.id} info={product} />
              ))}
            </div>

            {/* Pagination Buttons */}
            {totalPages > 1 && (
              <nav aria-label="Page navigation example" className="mt-4">
                <ul className="pagination d-flex justify-content-center">
                  {page > 1 && (
                    <>
                      <li className="page-item">
                        <a className="page-link" href={`/search/${category}/${text}?page=${page - 1}`}>Previous</a>
                      </li>
                      <li className="page-item">
                        <a className="page-link" href={`/search/${category}/${text}?page=${page - 1}`}>{page - 1}</a>
                      </li>
                    </>
                  )}

                  <li className="page-item active">
                    <span className="page-link">{page}</span>
                  </li>
                  {page + 1 <= totalPages && (
                    <>
                      <li className="page-item">
                        <a className="page-link"  href={`/search/${category}/${text}?page=${page + 1}`}>{page + 1}</a>
                      </li>
                      <li className="page-item">
                        <a className="page-link"  href={`/search/${category}/${text}?page=${page + 1}`}>Next</a>
                      </li>
                    </>
                  )}
                </ul>
              </nav>
            )}
          </>
        )}
      </main>
    </>
  );
}
