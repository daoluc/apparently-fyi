"use client";

import { useState, useMemo } from "react";
import { api } from "@/trpc/react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";

export function WorldPopulationChart() {
  // Fetch world population data
  const worldPopulationQuery = api.getWorldPopulationData.useQuery();

  // Process data for the chart
  const chartData = useMemo(() => {
    if (!worldPopulationQuery.data || worldPopulationQuery.data.length === 0) return [];

    // Convert data to format expected by the chart
    return worldPopulationQuery.data.map(item => ({
      year: item.year,
      "World Population": Number(item.value), // Convert BigInt to Number for the chart
    }));
  }, [worldPopulationQuery.data]);

  // Format population values in billions with B suffix
  const formatPopulation = (value: number) => {
    const valueInBillions = value / 1000000000;
    // For values less than 1 billion, show more decimal places
    const decimalPlaces = valueInBillions < 1 ? 2 : 1;
    return `${valueInBillions.toFixed(decimalPlaces)}B`;
  };

  if (worldPopulationQuery.isPending) {
    return (
      <div className="card h-[500px] w-full flex items-center justify-center">
        <p className="text-gray-500">Loading world population data...</p>
      </div>
    );
  }

  if (worldPopulationQuery.error) {
    return (
      <div className="card h-[500px] w-full flex items-center justify-center">
        <p className="text-red-500">Error loading world population data. Please try again.</p>
      </div>
    );
  }

  if (worldPopulationQuery.data?.length === 0) {
    return (
      <div className="card h-[500px] w-full flex items-center justify-center">
        <p className="text-gray-500">No population data available. Please try again later.</p>
      </div>
    );
  }

  return (
    <div className="card h-[500px] w-full">
      <h2 className="text-xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-primary">
        World Population Growth
      </h2>
      <ResponsiveContainer width="100%" height="90%">
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="year" 
            label={{ value: 'Year', position: 'insideBottomRight', offset: -10 }}
          />
          <YAxis 
            tickFormatter={formatPopulation}
            label={{ value: 'Population (Billions)', angle: -90, position: 'insideLeft' }}
          />
          <Tooltip 
            formatter={(value: number) => [`${formatPopulation(value)}`, 'Population']}
            labelFormatter={(label) => `Year: ${label}`}
          />
          <Legend />
          <Line
            type="monotone"
            dataKey="World Population"
            stroke="#4F46E5"
            activeDot={{ r: 8 }}
            strokeWidth={2}
            dot={{ r: 3 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}