import "@/styles/globals.css";

import { GeistSans } from "geist/font/sans";
import { Metadata } from "next";
import { Toaster } from "react-hot-toast";

import { TRPCReactProvider } from "@/trpc/react";
import { Header } from "@/components/Header";

export const metadata: Metadata = {
  title: "Apparently.FYI",
  description: "Interactive visualization of global population trends",
  icons: [
    // place favicon.ico in public folder and uncomment the following line
    // { rel: "icon", url: "/favicon.ico" }
  ],
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${GeistSans.variable}`}>
      <body className="min-h-screen bg-gray-50">
        <TRPCReactProvider>
          <Header />
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
          <Toaster />
        </TRPCReactProvider>
      </body>
    </html>
  );
}
