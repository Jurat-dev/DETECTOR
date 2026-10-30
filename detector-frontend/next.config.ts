import type { NextConfig } from "next";

// Backend (FastAPI) shu kompyuterda 8000-portda ishlaydi.
// Brauzer /api/... ga murojaat qiladi, Next.js uni backendga uzatadi.
// Shunda tunnel orqali bitta havola yetarli bo'ladi.
const BACKEND = process.env.BACKEND_INTERNAL_URL || "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${BACKEND}/:path*` }];
  },
};
export default nextConfig;
