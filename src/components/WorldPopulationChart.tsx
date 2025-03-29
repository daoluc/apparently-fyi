"use client";

import { useMemo } from "react";
import { api } from "@/trpc/react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

export function WorldPopulationChart() {
  // Fetch world population data
  const worldPopulationQuery = api.getWorldPopulationData.useQuery();

  // Process data for the chart and create Highcharts options
  const chartOptions: Highcharts.Options = useMemo(() => {
    if (!worldPopulationQuery.data || worldPopulationQuery.data.length === 0) {
      return {
        series: [{
          type: 'line',
          name: 'World Population',
          data: []
        }]
      };
    }

    // Convert data to format expected by Highcharts
    const data = worldPopulationQuery.data.map(item => [
      item.year,
      Number(item.value)
    ]);

    return {
      title: {
        text: undefined
      },
      chart: {
        type: 'line',
        style: {
          fontFamily: 'inherit'
        }
      },
      xAxis: {
        title: {
          text: 'Year'
        }
      },
      yAxis: {
        title: {
          text: 'Population (Billions)',
          rotation: -90
        },
        labels: {
          formatter: function(this: Highcharts.AxisLabelsFormatterContextObject): string {
            const value = typeof this.value === 'number' ? this.value : 0;
            return (value / 1000000000).toFixed(value < 1000000000 ? 2 : 1) + 'B';
          }
        }
      },
      tooltip: {
        pointFormatter: function(this: Highcharts.Point): string {
          const y = typeof this.y === 'number' ? this.y : 0;
          const valueInBillions = y / 1000000000;
          const decimalPlaces = valueInBillions < 1 ? 2 : 1;
          return `Population: ${valueInBillions.toFixed(decimalPlaces)}B`;
        }
      },
      series: [{
        type: 'line',
        name: 'World Population',
        data: data,
        color: '#4F46E5',
        marker: {
          radius: 3
        }
      }],
      credits: {
        enabled: false
      }
    };
  }, [worldPopulationQuery.data]);

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
      <div className="h-[90%]">
        <HighchartsReact
          highcharts={Highcharts}
          options={chartOptions}
        />
      </div>
    </div>
  );
}