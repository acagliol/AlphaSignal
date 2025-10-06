/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  // Performance optimizations
  experimental: {
    optimizeCss: false, // Disable CSS optimization in dev
  },
  // Disable font optimization warnings
  optimizeFonts: false,
  // Speed up dev server
  reactStrictMode: false,
}

export default nextConfig
