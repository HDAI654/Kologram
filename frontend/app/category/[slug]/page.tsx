import React from 'react';
import baseURL from "@/app/BaseURL";
import Product from '@/app/component/Product';
import MainNavbar from '@/app/component/MainNav';
import NoPrdFound from '@/app/component/NoPrdFound';

type Props = {
  params: { slug: string };
  searchParams?: { [key: string]: string | string[] | undefined };
};

// generate metadata
export async function generateMetadata({ params }: Props) {
  return {
    title: `${params.slug} | Shop`,
    description: `Browse products in category ${params.slug}`,
    openGraph: {
      title: `${params.slug} | Shop`,
      description: `Browse products in category ${params.slug}`,
      url: `https://kologram.com/category/${params.slug}`,
      type: 'website',
    },
    robots: 'index, follow',
  };
}

// get products based on category
async function fetchProducts(category: string, page: number) {
  if (page < 1) {
    return { products: [], totalPages: 0 };
  }
  const res = await fetch(baseURL + `/prd-api/search-prd/?category=${category}&page=${page-1}`, {
    next: { revalidate: 600 }, // revalidate after 60 seconds (ISR)
  });
  if (!res.ok) {
    throw new Error('Failed to fetch products');
  }
  const data = await res.json();
  return {products: data.products || [], totalPages: data.totalPages || 0};
}

// create static parametrs
export async function generateStaticParams() {
    try{
        const res = await fetch(baseURL + '/prd-api/getCategories/');
        if (!res.ok) {
            return [];
        }
        const data = await res.json();
        const categories = data.data.categories.map((c: [string, string]) => c[0]);

        return categories.map((slug: string) => ({ slug }));
    } catch (error) {
        return [];
    }
}


// Page
export default async function CategoryPage({ params, searchParams }: Props) {
  const page = Math.max(1, parseInt(searchParams?.page as string || '1'));
  const {products, totalPages} = await fetchProducts(params.slug, page);

  return (
    <>
        {/* Top Navbar */}
        <MainNavbar />

        {/* Main Content */}
        <main style={{ padding: '2rem', paddingTop: '100px', paddingBottom: '100px' }}>
            {/* Main Header */}
            <div className='row w-100 mb-4'>
                <div className="col-12 text-wrap text-center my-auto">
                    <h1 className="display-4">
                        {params.slug} 
                    </h1>
                </div>
            </div>

            {products.length === 0 ? (
            <NoPrdFound />
            ) : (
              <>
                {/* Product List */}
                <div className="row">
                    {products.map((product: any) => (
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
                            <a className="page-link" href={`/category/${params.slug}?page=${page - 1}`}>Previous</a>
                          </li>
                          <li className="page-item">
                            <a className="page-link" href={`/category/${params.slug}?page=${page - 1}`}>{page - 1}</a>
                          </li>
                        </>
                      )}

                      <li className="page-item active">
                        <span className="page-link">{page}</span>
                      </li>
                      {page + 1 <= totalPages && (
                        <>
                          <li className="page-item">
                            <a className="page-link" href={`/category/${params.slug}?page=${page + 1}`}>{page + 1}</a>
                          </li>
                          <li className="page-item">
                            <a className="page-link" href={`/category/${params.slug}?page=${page + 1}`}>Next</a>
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
