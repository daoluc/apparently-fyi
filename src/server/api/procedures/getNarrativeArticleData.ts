import { procedure } from "@/server/api/trpc";
import { z } from "zod";
import fs from "fs";
import path from "path";
import { parse } from "csv-parse/sync";

// Define schema for narrative article data
const narrativeArticleItemSchema = z.object({
  narrativeId: z.number(),
  articleId: z.number(),
  agreementScore: z.number(),
  title: z.string(),
  mediaLocation: z.string().nullable(),
  publishedDate: z.string().nullable(),
});

export const getNarrativeArticleData = procedure
  .output(z.array(narrativeArticleItemSchema))
  .query(async () => {
    try {
      // Path to the CSV file
      const csvFilePath = path.join(
        process.cwd(),
        "combined_narrative_articles.csv",
      );

      // Check if file exists
      if (!fs.existsSync(csvFilePath)) {
        console.error("CSV file not found:", csvFilePath);
        return [];
      }

      // Read and parse the CSV file
      const fileContent = fs.readFileSync(csvFilePath, "utf8");
      const records = parse(fileContent, {
        columns: true,
        skip_empty_lines: true,
      });

      // Transform the data to match our schema
      const narrativeArticleData = records.map((record: any) => ({
        narrativeId: parseInt(record["narrative_id"], 10),
        articleId: parseInt(record["article_id"], 10),
        agreementScore: parseFloat(record["agreement_score"]),
        title: record["Title"] || "",
        mediaLocation: record["Media Location"] || null,
        publishedDate: record["Published Date"] || null,
      }));

      return narrativeArticleData;
    } catch (error) {
      console.error("Error in getNarrativeArticleData procedure:", error);
      // Return an empty array instead of throwing to prevent UI crashes
      return [];
    }
  });
