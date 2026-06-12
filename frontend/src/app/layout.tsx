import type { Metadata } from 'next'
import { Navbar } from '@/components/Navbar'
import './globals.css'

export const metadata: Metadata = {
  title: 'Model Pricing Observatory',
  description: 'Track AI model pricing across providers and channels',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0a0a0a] text-gray-100 antialiased">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 py-6">{children}</main>
      </body>
    </html>
  )
}
