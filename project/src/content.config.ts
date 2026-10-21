import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const memos = defineCollection({
  loader: glob({ base: './src/content/memos', pattern: '**/*.md' }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    minutes: z.number().int().positive(),
  }),
});

export const collections = { memos };
