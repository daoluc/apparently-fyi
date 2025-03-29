"use client";

import { WorldPopulationChart } from "@/components/WorldPopulationChart";
import { ArticleDataProvider } from "@/components/ArticleDataProvider";
import { ArticleSparkline } from "@/components/ArticleSparkline";

export default function Home() {
  return (
    <main>
      <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-primary">
              Global Population Trends
            </h1>
            <p className="mt-2 text-gray-600">
              Explore population data across different regions and time periods
            </p>
          </div>

          {/* World Population Overview */}
          <div className="mb-12">
            <h2 className="text-2xl font-semibold mb-4">World Population Overview</h2>
            <p className="text-gray-600 mb-6">
              The chart below shows the total world population growth over time.
            </p>
            <WorldPopulationChart />
          </div>

          {/* Article Distribution */}
          <div className="mb-12">
            <h2 className="text-2xl font-semibold mb-4">Article Distribution</h2>
            <p className="text-gray-600 mb-6">
              Distribution of articles over time.
            </p>
            <ArticleDataProvider>
              <ArticleSparkline />
            </ArticleDataProvider>
          </div>
        </div>
      </div>
    </main>
  );
}
