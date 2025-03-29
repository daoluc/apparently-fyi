import { z } from "zod";
import { env } from "@/env";

// World Bank API response schemas
const worldBankIndicatorResponseSchema = z.array(
  z.object({
    indicator: z.object({
      id: z.string(),
      value: z.string(),
    }),
    country: z.object({
      id: z.string(),
      value: z.string(),
    }),
    countryiso3code: z.string(),
    date: z.string(),
    value: z.number().nullable(),
    unit: z.string().optional(),
    obs_status: z.string().optional(),
    decimal: z.number().optional(),
  }),
);

// Simple in-memory cache with expiration
const cache = new Map<string, { data: unknown; expiry: number }>();

function getCachedData<T>(key: string): T | null {
  const cachedItem = cache.get(key);
  if (cachedItem && cachedItem.expiry > Date.now()) {
    return cachedItem.data as T;
  }
  return null;
}

function setCachedData(key: string, data: unknown, ttlMs = 3600000): void {
  cache.set(key, {
    data,
    expiry: Date.now() + ttlMs,
  });
}

// Helper function to fetch data from World Bank API
async function fetchFromWorldBank<T>(
  endpoint: string,
  schema: z.ZodType<T>,
  params: Record<string, string> = {},
): Promise<T> {
  const cacheKey = `${endpoint}:${JSON.stringify(params)}`;
  const cachedData = getCachedData<T>(cacheKey);

  if (cachedData) {
    return cachedData;
  }

  // Build query string
  const queryParams = new URLSearchParams({
    format: "json",
    ...params,
  });

  const url = `https://api.worldbank.org/v2/${endpoint}?${queryParams.toString()}`;

  try {
    const response = await fetch(url);

    if (!response.ok) {
      throw new Error(
        `World Bank API error: ${response.status} ${response.statusText}`,
      );
    }

    const data = (await response.json()) as [unknown, unknown[]];

    // Check if the response is paginated
    if (
      Array.isArray(data) &&
      data.length >= 2 &&
      typeof data[0] === "object" &&
      data[0] !== null
    ) {
      const metadata = data[0] as { page: number; pages: number };

      // If this is a paginated response and there are more pages
      if (
        "page" in metadata &&
        "pages" in metadata &&
        metadata.page < metadata.pages
      ) {
        // We need to fetch all pages and combine them
        const allResults = [...data[1]];
        const totalPages = metadata.pages;

        // Fetch remaining pages
        for (let page = 2; page <= totalPages; page++) {
          const pageParams = new URLSearchParams({
            ...params,
            page: page.toString(),
          });

          const pageUrl = `https://api.worldbank.org/v2/${endpoint}?${pageParams.toString()}`;
          const pageResponse = await fetch(pageUrl);

          if (!pageResponse.ok) {
            throw new Error(
              `World Bank API error on page ${page}: ${pageResponse.status} ${pageResponse.statusText}`,
            );
          }

          const pageData = await pageResponse.json();

          if (
            Array.isArray(pageData) &&
            pageData.length >= 2 &&
            Array.isArray(pageData[1])
          ) {
            allResults.push(...pageData[1]);
          }
        }

        // Replace the original data's second element with the combined results
        data[1] = allResults;
      }
    }

    const parsedData = schema.parse(data[1]);

    // Cache the result
    setCachedData(cacheKey, parsedData, env.WORLD_BANK_API_CACHE_TTL);

    return parsedData;
  } catch (error) {
    console.error("Error fetching data from World Bank API:", error);
    throw error;
  }
}

// Population indicator code for World Bank API
const POPULATION_INDICATOR = "SP.POP.TOTL";

// Get world population data
export async function getWorldPopulationData() {
  const currentYear = new Date().getFullYear();
  const startYear = 1900; // Updated to fetch data from 1900
  const endYear = currentYear - 1; // Most recent complete year

  const params: Record<string, string> = {
    date: `${startYear}:${endYear}`,
    per_page: "1000", // Request a large page size to minimize pagination
  };

  // World aggregate has code "WLD"
  const endpoint = `country/WLD/indicator/${POPULATION_INDICATOR}`;

  try {
    const response = await fetchFromWorldBank(
      endpoint,
      worldBankIndicatorResponseSchema,
      params,
    );

    const indicatorData = response;

    // Transform data to match our simplified format
    // Check if indicatorData is an array before using map
    const worldPopulationData = Array.isArray(indicatorData)
      ? indicatorData.map((item: { value: number | null; date: string }) => {
          // Convert population value to BigInt to match our existing format
          // If value is null, use 0
          const populationValue =
            item.value !== null ? BigInt(Math.round(item.value)) : BigInt(0);

          return {
            year: parseInt(item.date),
            value: populationValue,
          };
        })
      : [];

    // Sort by year
    return worldPopulationData.sort(
      (a: { year: number }, b: { year: number }) => a.year - b.year,
    );
  } catch (error) {
    console.error("Error getting world population data:", error);
    // Return an empty array instead of throwing to prevent UI crashes
    return [];
  }
}

// Get available year range for population data
export async function getYearRange() {
  // Updated to reflect that we now fetch data from 1900
  const currentYear = new Date().getFullYear();

  return {
    minYear: 1900,
    maxYear: currentYear - 1,
  };
}
