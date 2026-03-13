import { z } from 'zod';

export const AuthTokens = z.object({
  access: z.string(),
  refresh: z.string()
});
export type AuthTokens = z.infer<typeof AuthTokens>;

export const User = z.object({
  id: z.number(),
  username: z.string()
});
export type User = z.infer<typeof User>;

export const Space = z.object({
  id: z.number(),
  key: z.string(),
  name: z.string()
});
export type Space = z.infer<typeof Space>;

export const Page = z.object({
  id: z.number(),
  slug: z.string(),
  title: z.string(),
  content: z.string().optional()
});
export type Page = z.infer<typeof Page>;
