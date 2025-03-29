import { procedure } from "@/server/api/trpc";
import { getWorldPopulationData as fetchWorldPopulationData } from "@/lib/server/worldBankApi";
import { z } from "zod";

// Define a schema for the population data items
const populationDataItemSchema = z.object({
  year: z.number(),
  value: z.bigint(),
});

export const getWorldPopulationData = procedure
  .output(z.array(populationDataItemSchema))
  .query(async () => {
    try {
      // Fetch world population data from World Bank API
      const worldPopulationData = await fetchWorldPopulationData();
      
      // Ensure we're returning an array
      return Array.isArray(worldPopulationData) ? worldPopulationData : [];
    } catch (error) {
      console.error("Error in getWorldPopulationData procedure:", error);
      // Return an empty array instead of throwing to prevent UI crashes
      return [];
    }
  });