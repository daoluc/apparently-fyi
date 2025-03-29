import { db } from "@/server/db";

// Sample world population data (in billions, to be converted to actual numbers)
const worldPopulationData = [
  { year: 1950, value: 2.5 },
  { year: 1960, value: 3.0 },
  { year: 1970, value: 3.7 },
  { year: 1980, value: 4.4 },
  { year: 1990, value: 5.3 },
  { year: 2000, value: 6.1 },
  { year: 2010, value: 6.9 },
  { year: 2020, value: 7.8 },
];

/**
 * Seeds the database with sample world population data
 * This is for development purposes only
 */
export async function seedPopulationData() {
  console.log("Seeding world population data...");
  
  // Create world population data
  for (const data of worldPopulationData) {
    // Convert billions to actual number
    const value = BigInt(data.value * 1000000000);
    
    await db.worldPopulationData.upsert({
      where: {
        year: data.year,
      },
      update: { value },
      create: {
        year: data.year,
        value,
      },
    });
  }
  
  console.log("World population data seeding complete!");
}