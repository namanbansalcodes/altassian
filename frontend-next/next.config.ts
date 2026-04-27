import type {NextConfig} from "next";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

const securityHeaders = [
  {key: "Strict-Transport-Security", value: "max-age=31536000; includeSubDomains; preload"},
  {key: "X-Frame-Options", value: "DENY"},
  {key: "X-Content-Type-Options", value: "nosniff"},
  {key: "Referrer-Policy", value: "same-origin"},
  {key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()"},
];

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {source: "/api/:path*", destination: `${apiBase}/api/:path*`},
    ];
  },
  async headers() {
    return [{source: "/:path*", headers: securityHeaders}];
  },
  reactStrictMode: true,
  experimental: {typedRoutes: true},
};

export default nextConfig;
