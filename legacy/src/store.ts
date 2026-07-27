import type { TicketStatus } from "./schemas.js";

export type AsyncTicketRecord = {
  id: string;
  tenantId: string;
  status: TicketStatus;
  createdAt: number;
  updatedAt: number;
  fastPathSummary: {
    classification: string;
    confidence: number;
    suggestedSteps: string[];
  };
  agentId?: string;
  runId?: string;
  deepResultText?: string;
  deepError?: string;
};

const tickets = new Map<string, AsyncTicketRecord>();

function now() {
  return Date.now();
}

export function createTicketRecord(
  id: string,
  tenantId: string,
  summary: AsyncTicketRecord["fastPathSummary"],
): AsyncTicketRecord {
  const rec: AsyncTicketRecord = {
    id,
    tenantId,
    status: "pending",
    createdAt: now(),
    updatedAt: now(),
    fastPathSummary: summary,
  };
  tickets.set(id, rec);
  return rec;
}

export function getTicketRecord(id: string): AsyncTicketRecord | undefined {
  return tickets.get(id);
}

export function patchTicketRecord(
  id: string,
  patch: Partial<
    Pick<
      AsyncTicketRecord,
      | "status"
      | "agentId"
      | "runId"
      | "deepResultText"
      | "deepError"
    >
  >,
): AsyncTicketRecord | undefined {
  const cur = tickets.get(id);
  if (!cur) return undefined;
  const next: AsyncTicketRecord = {
    ...cur,
    ...patch,
    updatedAt: now(),
  };
  tickets.set(id, next);
  return next;
}
