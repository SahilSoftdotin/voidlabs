import type { Metadata, Viewport } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'VOIDLABS — Creative Studio | Brand Identity & Digital Design',
  description: 'VOIDLAB is a creative studio crafting experiences at the intersection of design and technology. We specialize in brand identity, UI/UX design, and digital innovation.',
  keywords: ['creative studio', 'design agency', 'brand identity', 'UI/UX design', 'digital design', 'branding'],
  authors: [{ name: 'VOIDLAB Creative Studio' }],
  creator: 'VOIDLAB',
  publisher: 'VOIDLAB',
  robots: 'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1',
  alternates: {
    canonical: 'https://sahilsoftdotin.github.io/voidlabs/',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://sahilsoftdotin.github.io/voidlabs/',
    title: 'VOIDLABS — Creative Studio',
    description: 'Creative experiences at the intersection of design and technology',
    siteName: 'VOIDLABS',
    images: [
      {
        url: 'https://sahilsoftdotin.github.io/voidlabs/og-image.jpg',
        width: 1200,
        height: 630,
        alt: 'VOIDLAB Creative Studio',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'VOIDLABS — Creative Studio',
    description: 'Craft futures worth seeing',
    creator: '@voidlab',
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'VOIDLABS',
  },
  formatDetection: {
    telephone: false,
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
  themeColor: '#0a0a14',
  colorScheme: 'dark',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <link rel="icon" href="/voidlabs/favicon.ico" />
        <link rel="apple-touch-icon" href="/voidlabs/apple-touch-icon.png" />
        <link rel="manifest" href="/voidlabs/manifest.json" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Organization',
              name: 'VOIDLAB',
              description: 'Creative studio crafting experiences at the intersection of design and technology',
              url: 'https://sahilsoftdotin.github.io/voidlabs/',
              logo: 'https://sahilsoftdotin.github.io/voidlabs/logo.png',
              sameAs: [
                'https://github.com/SahilSoftdotin',
              ],
            }),
          }}
        />
      </head>
      <body className="bg-void text-white antialiased">
        <div className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
