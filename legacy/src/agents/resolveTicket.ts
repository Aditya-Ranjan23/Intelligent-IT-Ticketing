import { Agent, CursorAgentError } from "@cursor/sdk";
import { patchTicketRecord } from "../store.js";

function apiKey(): string | undefined {
  const k = process.env.CURSOR_API_KEY?.trim();
  return k || undefined;
}

function modelConfig() {
  const id = process.env.CURSOR_MODEL_ID?.trim() || "composer-2";
  return { id };
}

function buildPrompt(payload: {
  tenantId: string;
  normalizedText: string;
  logSnippet?: string;
  repoUrl?: string;
}): string {
  return [
    "You are an enterprise IT support assistant. Reply concisely.",
    "Given the ticket below, propose numbered remediation steps (max 8). No code edits required.",
    `Tenant: ${payload.tenantId}`,
    payload.repoUrl ? `Related repo (context only): ${payload.repoUrl}` : "",
    "Ticket:",
    payload.normalizedText,
    payload.logSnippet ? `Log excerpt:\n${payload.logSnippet.slice(0, 6000)}` : "",
  ]
    .filter(Boolean)
    .join("\n\n");
}

/**
 * Runs SDK deep resolution in the background. Updates the in-memory ticket record.
 * Always disposes the agent; distinguishes startup failure vs run failure.
 */
export async function startDeepResolutionJob(args: {
  ticketId: string;
  tenantId: string;
  normalizedText: string;
  logSnippet?: string;
  repoUrl?: string;
  cwd: string;
}): Promise<void> {
  const key = apiKey();
  if (!key) {
    patchTicketRecord(args.ticketId, {
      status: "deep_resolution_error",
      deepError: "CURSOR_API_KEY is not set; skipping SDK deep resolution.",
    });
    return;
  }

  patchTicketRecord(args.ticketId, { status: "deep_resolution_running" });

  const prompt = buildPrompt({
    tenantId: args.tenantId,
    normalizedText: args.normalizedText,
    logSnippet: args.logSnippet,
    repoUrl: args.repoUrl,
  });

  const agent = await Agent.create({
    apiKey: key,
    model: modelConfig(),
    local: { cwd: args.cwd, settingSources: [] },
  });

  try {
    const run = await agent.send(prompt);
    console.info(
      `[sdk] deep-resolve ticket=${args.ticketId} agentId=${agent.agentId} runId=${run.id}`,
    );

    patchTicketRecord(args.ticketId, {
      agentId: agent.agentId,
      runId: run.id,
    });

    if (run.supports("stream")) {
      for await (const _ of run.stream()) {
        /* drain for completeness; demo does not stream to client */
      }
    }

    const result = await run.wait();
    if (result.status === "error") {
      patchTicketRecord(args.ticketId, {
        status: "deep_resolution_error",
        deepError: `Run finished with error status (run=${run.id})`,
      });
      return;
    }

    const text = runResultText(result);
    patchTicketRecord(args.ticketId, {
      status: "deep_resolution_finished",
      deepResultText: text || "(empty assistant text)",
    });
  } catch (err) {
    if (err instanceof CursorAgentError) {
      patchTicketRecord(args.ticketId, {
        status: "deep_resolution_error",
        deepError: `CursorAgentError: ${err.message} (retryable=${err.isRetryable})`,
      });
      return;
    }
    patchTicketRecord(args.ticketId, {
      status: "deep_resolution_error",
      deepError: err instanceof Error ? err.message : String(err),
    });
  } finally {
    await agent[Symbol.asyncDispose]();
  }
}

/** One-shot deep resolution (blocks until done). Useful for scripts/tests. */
export async function deepResolveOneShot(args: {
  tenantId: string;
  normalizedText: string;
  logSnippet?: string;
  repoUrl?: string;
  cwd: string;
}): Promise<{ ok: true; text: string } | { ok: false; error: string }> {
  const key = apiKey();
  if (!key) {
    return { ok: false, error: "CURSOR_API_KEY is not set" };
  }
  const prompt = buildPrompt({
    tenantId: args.tenantId,
    normalizedText: args.normalizedText,
    logSnippet: args.logSnippet,
    repoUrl: args.repoUrl,
  });
  try {
    const result = await Agent.prompt(prompt, {
      apiKey: key,
      model: modelConfig(),
      local: { cwd: args.cwd, settingSources: [] },
    });
    if (result.status === "error") {
      return { ok: false, error: "Agent.prompt completed with error status" };
    }
    const text = runResultText(result);
    return { ok: true, text: text || "" };
  } catch (err) {
    if (err instanceof CursorAgentError) {
      return { ok: false, error: `CursorAgentError: ${err.message}` };
    }
    return { ok: false, error: err instanceof Error ? err.message : String(err) };
  }
}

function runResultText(result: { result?: string }): string {
  return typeof result.result === "string" ? result.result.trim() : "";
}
