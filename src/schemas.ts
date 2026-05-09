import { z } from "zod";

export const resolveTicketBodySchema = z.object({
  tenantId: z.string().min(1),
  text: z.string().default(""),
  imageBase64: z.string().optional(),
  logSnippet: z.string().optional(),
  repoUrl: z.string().url().optional(),
});

export type ResolveTicketBody = z.infer<typeof resolveTicketBodySchema>;

export const ticketStatusSchema = z.enum([
  "pending",
  "deep_resolution_running",
  "deep_resolution_finished",
  "deep_resolution_error",
]);

export type TicketStatus = z.infer<typeof ticketStatusSchema>;
