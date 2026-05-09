import { randomUUID } from "node:crypto";
import { serve } from "@hono/node-server";
import { Hono } from "hono";
import { startDeepResolutionJob } from "./agents/resolveTicket.js";
import { runFastPath } from "./fastPath.js";
import { resolveTicketBodySchema } from "./schemas.js";
import { createTicketRecord, getTicketRecord } from "./store.js";

const app = new Hono();

function confidenceThreshold(): number {
  const raw = process.env.CONFIDENCE_THRESHOLD;
  const n = raw ? Number(raw) : 0.72;
  return Number.isFinite(n) ? n : 0.72;
}

app.get("/health", (c) => c.json({ ok: true }));

app.post("/tickets/resolve", async (c) => {
  const started = performance.now();
  let body: unknown;
  try {
    body = await c.req.json();
  } catch {
    return c.json({ error: "Invalid JSON body" }, 400);
  }

  const parsed = resolveTicketBodySchema.safeParse(body);
  if (!parsed.success) {
    return c.json({ error: parsed.error.flatten() }, 400);
  }

  const input = parsed.data;
  const fast = runFastPath({
    text: input.text,
    imageBase64: input.imageBase64,
    logSnippet: input.logSnippet,
  });

  const latencyMs = Math.round(performance.now() - started);
  const threshold = confidenceThreshold();
  const needsDeep =
    fast.confidence < threshold || fast.classification === "UNKNOWN_ESCALATION";

  if (!needsDeep) {
    return c.json({
      ticketId: null,
      latencyMs,
      classification: fast.classification,
      confidence: fast.confidence,
      suggestedSteps: fast.suggestedSteps,
      hasScreenshot: fast.hasScreenshot,
      ocrHint: fast.ocrHint,
      resolutionMode: "fast_complete",
      deepResolution: null,
    });
  }

  const ticketId = randomUUID();
  createTicketRecord(ticketId, input.tenantId, {
    classification: fast.classification,
    confidence: fast.confidence,
    suggestedSteps: fast.suggestedSteps,
  });

  const cwd = process.cwd();
  void startDeepResolutionJob({
    ticketId,
    tenantId: input.tenantId,
    normalizedText: fast.normalizedText,
    logSnippet: input.logSnippet,
    repoUrl: input.repoUrl,
    cwd,
  }).catch((err) => {
    console.error("[deep-resolve] unhandled", err);
  });

  return c.json({
    ticketId,
    latencyMs,
    classification: fast.classification,
    confidence: fast.confidence,
    suggestedSteps: fast.suggestedSteps,
    hasScreenshot: fast.hasScreenshot,
    ocrHint: fast.ocrHint,
    resolutionMode: "fast_plus_deep_pending",
    deepResolution: {
      pollPath: `/tickets/${ticketId}/status`,
      note: "First response within SLO; Cursor SDK agent runs asynchronously.",
    },
  });
});

app.get("/tickets/:id/status", (c) => {
  const id = c.req.param("id");
  const rec = getTicketRecord(id);
  if (!rec) return c.json({ error: "Unknown ticket id" }, 404);
  return c.json({
    id: rec.id,
    tenantId: rec.tenantId,
    status: rec.status,
    updatedAt: rec.updatedAt,
    fastPath: rec.fastPathSummary,
    agentId: rec.agentId,
    runId: rec.runId,
    deepResultText: rec.deepResultText,
    deepError: rec.deepError,
  });
});

const port = Number(process.env.PORT) || 3000;
console.info(`[ticket-api] listening on http://127.0.0.1:${port}`);
serve({ fetch: app.fetch, port });
