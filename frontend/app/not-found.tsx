import React from 'react'
import Link from 'next/link'
import { Metadata } from 'next'
import "bootstrap/dist/css/bootstrap.min.css";

export const metadata: Metadata = {
  title: 'Kologram - 404',
  description: 'Your page is not found',
}

export default function NotFound() {
  return (
    <main className="flex flex-col items-center justify-center h-screen text-center p-4">
      <h1 className="text-4xl font-bold mb-4">404 - Page is not found</h1>
      <p className="text-lg mb-6"> The address is not correct</p>
      <Link href="/" className="text-blue-500 underline hover:text-blue-700 transition">
        Back to Home
      </Link>
    </main>
  )
}
