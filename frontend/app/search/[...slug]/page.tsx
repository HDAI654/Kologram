import SearchPage from './SearchPage';

// create metadata for the page
export const dynamic = 'force-dynamic';
export async function generateMetadata({ params }: { params: { slug?: string[] } }) {
  const [category = 'all', text = ''] = params.slug || [];

  const title = `Search results for "${text}" in ${category}`;
  const description = `Find the best deals in ${category} category related to "${text}". Compare prices, reviews and more.`;

  return {
    title,
    description,
    openGraph: {
      title,
      description,
      url: `https://kologram.com/search/${category}/${text}`,
      type: 'website',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
    robots: 'index, follow',
  };
}

export default function Page() {
  return <SearchPage />;
}
