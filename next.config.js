/** @type {import('next').NextConfig} */
const isProduction = process.env.NODE_ENV === 'production';

const nextConfig = {
  reactStrictMode: true,
  output: 'export',
  basePath: isProduction ? '/voidlabs' : '',
  assetPrefix: isProduction ? '/voidlabs' : '',
  images: {
    unoptimized: true,
    formats: ['image/webp', 'image/avif'],
  },
  poweredByHeader: false,
  compress: true,
  productionBrowserSourceMaps: false,
  trailingSlash: false,
  experimental: {
    optimizePackageImports: ['react', 'react-dom'],
  },
};

export default nextConfig;
