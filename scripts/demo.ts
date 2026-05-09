const base = process.env.TICKET_API_URL ?? "http://127.0.0.1:3000";

type ResolveResponse = {
  ticketId: string | null;
  latencyMs: number;
  classification: string;
  confidence: number;
  suggestedSteps: string[];
  resolutionMode: string;
  hasScreenshot?: boolean;
};

async function post(body: unknown): Promise<ResolveResponse> {
  const res = await fetch(`${base}/tickets/resolve`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const t = await res.text();
    throw new Error(`HTTP ${res.status}: ${t}`);
  }
  return (await res.json()) as ResolveResponse;
}

type StatusPayload = {
  status: string;
  deepResultText?: string;
  deepError?: string;
  agentId?: string;
  runId?: string;
};

async function pollStatus(
  ticketId: string,
  maxWaitMs: number,
): Promise<StatusPayload | { status: "timeout" }> {
  const deadline = Date.now() + maxWaitMs;
  while (Date.now() < deadline) {
    const res = await fetch(`${base}/tickets/${ticketId}/status`);
    if (!res.ok) throw new Error(`status ${res.status}`);
    const j = (await res.json()) as StatusPayload;
    if (
      j.status === "deep_resolution_finished" ||
      j.status === "deep_resolution_error"
    ) {
      return j;
    }
    await new Promise((r) => setTimeout(r, 800));
  }
  return { status: "timeout" };
}

async function main() {
  console.info(`Demo against ${base}\n`);

  const cases = [
    {
      name: "high-confidence VPN (fast path)",
      body: {
        tenantId: "demo-tenant",
        text: "My VPN disconnects constantly when using AnyConnect.",
      },
    },
    {
      name: "noisy / unknown (expect deep path if API key set)",
      body: {
        tenantId: "demo-tenant",
        text: "the thing is broken please help",
      },
    },
    {
      name: "screenshot-primary ticket",
      body: {
        tenantId: "demo-tenant",
        text: "see attached",
        imageBase64: Buffer.from("fake-png-bytes-for-demo").toString("base64"),
      },
    },
  ];

  for (const c of cases) {
    console.info(`--- ${c.name} ---`);
    const t0 = performance.now();
    const r = await post(c.body);
    console.info(
      `latencyMs=${r.latencyMs} wallMs=${Math.round(performance.now() - t0)} mode=${r.resolutionMode} class=${r.classification} conf=${r.confidence.toFixed(3)}`,
    );
    console.info("steps:", r.suggestedSteps.slice(0, 2).join(" | "));

    if (r.ticketId && r.resolutionMode === "fast_plus_deep_pending") {
      console.info("polling deep resolution…");
      const st = await pollStatus(r.ticketId, 120_000);
      console.info("final status object:", st);
    }
    console.info("");
  }
}

main().catch((e) => {
  console.error(e);
  console.error(
    "\nStart the API in another terminal: npm run start\nOr set TICKET_API_URL.",
  );
  process.exitCode = 1;
});
