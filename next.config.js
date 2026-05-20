/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export',  // Enable static export
  basePath: '/voidlabs',  // GitHub Pages subdirectory
  assetPrefix: '/voidlabs',  // Prefix for assets
};

export default nextConfig;
