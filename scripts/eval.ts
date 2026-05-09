import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { runFastPath } from "../src/fastPath.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

type Row = { text: string; expected: string };

function parseCsv(raw: string): Row[] {
  const lines = raw.split(/\r?\n/).filter((l) => l.trim().length > 0);
  const out: Row[] = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i]!;
    const firstComma = line.indexOf(",");
    if (firstComma === -1) continue;
    const text = line.slice(0, firstComma).replace(/^"|"$/g, "");
    const expected = line.slice(firstComma + 1).trim();
    out.push({ text, expected });
  }
  return out;
}

function main() {
  const csvPath = join(__dirname, "..", "eval", "data", "tickets-labeled.csv");
  const raw = readFileSync(csvPath, "utf8");
  const rows = parseCsv(raw);
  let top1 = 0;
  const mismatches: string[] = [];

  for (const row of rows) {
    const got = runFastPath({ text: row.text }).classification;
    if (got === row.expected) top1 += 1;
    else mismatches.push(`expected ${row.expected} got ${got} | ${row.text.slice(0, 60)}`);
  }

  const acc = rows.length ? top1 / rows.length : 0;
  console.info(`Offline eval: ${top1}/${rows.length} top-1 = ${(acc * 100).toFixed(1)}%`);
  if (mismatches.length) {
    console.info("Mismatches:");
    for (const m of mismatches) console.info(" -", m);
  }
  if (acc < 0.8) {
    console.error("Accuracy below 80% on this slice — tune PLAYBOOK or CSV.");
    process.exitCode = 2;
  }
}

main();
