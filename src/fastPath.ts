import { createHash } from "node:crypto";

export type FastPathResult = {
  classification: string;
  confidence: number;
  suggestedSteps: string[];
  hasScreenshot: boolean;
  normalizedText: string;
  ocrHint?: string;
};

type PlaybookEntry = {
  id: string;
  keywords: string[];
  suggestedSteps: string[];
  baseConfidence: number;
};

/** Tiny in-memory “runbook + resolved ticket” retrieval stub for the prototype. */
const PLAYBOOK: PlaybookEntry[] = [
  {
    id: "NET_VPN_DISCONNECT",
    keywords: ["vpn", "disconnect", "tunnel", "anyconnect", "globalprotect"],
    suggestedSteps: [
      "Restart the VPN client and reconnect to the preferred gateway.",
      "Clear saved VPN profile and re-import the enterprise profile from the IT portal.",
      "If Wi-Fi is unstable, switch to wired or another network and retry.",
    ],
    baseConfidence: 0.88,
  },
  {
    id: "MAIL_OUTLOOK_SYNC",
    keywords: ["outlook", "sync", "mailbox", "exchange", "email stuck"],
    suggestedSteps: [
      "Run Outlook in Safe Mode once, then restart normally.",
      "Repair Office from Apps & Features, then recreate the mail profile if needed.",
      "Confirm MFA / modern auth prompts are completed on mobile and desktop.",
    ],
    baseConfidence: 0.86,
  },
  {
    id: "ACC_PASSWORD_RESET",
    keywords: ["password", "reset", "locked", "login", "cannot sign in"],
    suggestedSteps: [
      "Use the self-service password portal; ensure CAPS LOCK is off.",
      "If AD lockout, wait 15 minutes or ask helpdesk for an unlock.",
      "Re-enroll MFA if the error references security defaults.",
    ],
    baseConfidence: 0.9,
  },
  {
    id: "HW_PRINT_SPOOLER",
    keywords: ["printer", "print", "spooler", "queue"],
    suggestedSteps: [
      "Clear the print queue and restart the Print Spooler service.",
      "Reinstall the printer driver from the manufacturer or corporate package.",
      "Verify the printer IP / queue name against the intranet printer list.",
    ],
    baseConfidence: 0.84,
  },
  {
    id: "APP_TEAMS_CRASH",
    keywords: ["teams", "crash", "freeze", "microsoft teams"],
    suggestedSteps: [
      "Fully quit Teams (system tray), clear cache %appdata%\\Microsoft\\Teams, relaunch.",
      "Update Teams and Windows; reboot if pending updates exist.",
      "If web works but desktop fails, use Teams web while desktop is repaired.",
    ],
    baseConfidence: 0.85,
  },
];

export function normalizeTicketText(raw: string): string {
  return raw
    .replace(/\s+/g, " ")
    .replace(/[^\p{L}\p{N}\s.,;:!?'"()-]/gu, " ")
    .trim()
    .slice(0, 8000);
}

function pseudoNoisePenalty(text: string): number {
  const h = createHash("sha256").update(text).digest()[0] ?? 0;
  return (h % 7) / 100;
}

/** Heuristic “OCR” placeholder when screenshot bytes are present (no real OCR in prototype). */
export function screenshotOcrHint(_imageBase64: string | undefined): string | undefined {
  if (!_imageBase64?.length) return undefined;
  return "[Screenshot attached — OCR pending; using subject/body cues only for this demo.]";
}

export function runFastPath(input: {
  text: string;
  imageBase64?: string;
  logSnippet?: string;
}): FastPathResult {
  const hasScreenshot = Boolean(input.imageBase64 && input.imageBase64.length > 40);
  const ocrHint = screenshotOcrHint(input.imageBase64);
  const combined = normalizeTicketText(
    [input.text, input.logSnippet ?? "", ocrHint ?? ""].filter(Boolean).join(" \n "),
  );
  const hay = combined.toLowerCase();

  let best: { entry: PlaybookEntry; score: number } | undefined;
  for (const entry of PLAYBOOK) {
    let score = 0;
    for (const kw of entry.keywords) {
      if (hay.includes(kw)) score += 1;
    }
    if (!best || score > best.score) best = { entry, score };
  }

  const noiseAdj = pseudoNoisePenalty(hay);

  if (best && best.score > 0) {
    const confidence = Math.min(
      0.97,
      Math.max(0.55, best.entry.baseConfidence - noiseAdj + best.score * 0.02),
    );
    return {
      classification: best.entry.id,
      confidence,
      suggestedSteps: best.entry.suggestedSteps,
      hasScreenshot,
      normalizedText: combined,
      ocrHint,
    };
  }

  return {
    classification: "UNKNOWN_ESCALATION",
    confidence: Math.max(0.2, 0.45 - noiseAdj),
    suggestedSteps: [
      "Collect exact error text, timestamp, and device name.",
      "Attach logs or a screenshot of the full error window.",
      "Route to L2 if the issue blocks work and no playbook matched.",
    ],
    hasScreenshot,
    normalizedText: combined,
    ocrHint,
  };
}
