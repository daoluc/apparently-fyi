"use client";

import Link from "next/link";

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center">
          <Link href="/" className="text-xl font-bold text-transparent bg-clip-text bg-gradient-primary">
            Apparently.FYI
          </Link>
        </div>
      </div>
    </header>
  );
}
