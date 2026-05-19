import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'VOIDLABS',
  description: 'Welcome to VOIDLABS - Exploring the void',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-void text-white">{children}</body>
    </html>
  )
}
