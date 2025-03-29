"use client";

import { useMemo } from "react";
import { api } from "@/trpc/react";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";

export function NarrativeScatterChart() {
  // Fetch narrative article data
  const narrativeArticleQuery = api.getNarrativeArticleData.useQuery();

  // Process data for the chart and create Highcharts options
  const chartOptions: Highcharts.Options = useMemo(() => {
    if (!narrativeArticleQuery.data || narrativeArticleQuery.data.length === 0) {
      return {
        series: [{
          type: 'scatter',
          name: 'Articles',
          data: []
        }]
      };
    }

    // Group data by media location
    const groupedByMedia = narrativeArticleQuery.data.reduce((acc, item) => {
      if (!item.publishedDate) return acc;

      const mediaLocation = item.mediaLocation || 'Unknown';
      if (!acc[mediaLocation]) {
        acc[mediaLocation] = [];
      }

      try {
        // Parse the date and convert to timestamp
        const date = new Date(item.publishedDate);
        if (!isNaN(date.getTime())) {
          acc[mediaLocation].push({
            x: date.getTime(),
            y: item.agreementScore,
            name: item.title,
            articleId: item.articleId,
            narrativeId: item.narrativeId
          });
        }
      } catch (e) {
        // Skip invalid dates
        console.warn("Invalid date:", item.publishedDate);
      }

      return acc;
    }, {} as Record<string, Array<{ x: number, y: number, name: string, articleId: number, narrativeId: number }>>);

    // Convert grouped data to series
    const series = Object.entries(groupedByMedia).map(([mediaLocation, data]) => ({
      type: 'scatter' as const,
      name: mediaLocation,
      data: data
    }));

    return {
      title: {
        text: undefined
      },
      chart: {
        type: 'scatter',
        style: {
          fontFamily: 'inherit'
        },
        zoomType: 'xy'
      },
      xAxis: {
        type: 'datetime',
        title: {
          text: 'Publication Date'
        }
      },
      yAxis: {
        title: {
          text: 'Agreement Score',
          rotation: -90
        },
        min: -1,
        max: 1
      },
      tooltip: {
        formatter: function () {
          const point = this.point as any;
          return `<b>${point.name}</b><br/>` +
            `Date: ${Highcharts.dateFormat('%Y-%m-%d', point.x)}<br/>` +
            `Agreement Score: ${point.y.toFixed(2)}<br/>` +
            `Media: ${this.series.name}`;
        }
      },
      plotOptions: {
        scatter: {
          marker: {
            radius: 5,
            states: {
              hover: {
                enabled: true,
                lineColor: 'rgb(100,100,100)'
              }
            }
          },
          states: {
            hover: {
              marker: {
                enabled: false
              }
            }
          }
        }
      },
      series: series,
      credits: {
        enabled: false
      }
    };
  }, [narrativeArticleQuery.data]);

  if (narrativeArticleQuery.isPending) {
    return (
      <div className="card h-[500px] w-full flex items-center justify-center">
        <p className="text-gray-500">Loading narrative article data...</p>
      </div>
    );
  }

  if (narrativeArticleQuery.error) {
    return (
      <div className="card h-[500px] w-full flex items-center justify-center">
        <p className="text-red-500">Error loading narrative article data. Please try again.</p>
      </div>
    );
  }

  if (narrativeArticleQuery.data?.length === 0) {
    return (
      <div className="card h-[500px] w-full flex items-center justify-center">
        <p className="text-gray-500">No narrative article data available. Please try again later.</p>
      </div>
    );
  }

  return (
    <div className="card h-[500px] w-full">
      <h2 className="text-xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-primary">
        Article Agreement Scores by Publication Date
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
