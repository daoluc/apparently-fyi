import { procedure } from "@/server/api/trpc";
import { getYearRange as fetchYearRange } from "@/lib/server/worldBankApi";

export const getYearRange = procedure.query(async () => {
  // Get year range from World Bank API
  const yearRange = await fetchYearRange();
  
  return yearRange;
});