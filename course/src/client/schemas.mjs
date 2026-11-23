import { z } from 'zod';

const credentials = z.object({ email: z.email(), password: z.string().min(10).max(128) });
export const formSchemas = {
  '#login': credentials,
  '#signup': credentials.extend({ nickname: z.string().trim().min(1).max(40) }),
  '#editor': z.object({
    id: z.string().regex(/^$|^[1-9]\d*$/), title: z.string().trim().min(1).max(200),
    body: z.string().trim().min(1).max(20000), tags: z.string(),
  }),
};
