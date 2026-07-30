#!/usr/bin/env node
// Render a deck spec to numbered 1080x1080 PNGs.
//
//   node visuals/render.mjs deck.json out/dir
//
// Deliberately dependency-free: writes the per-slide spec next to slide.html and
// drives the local Chrome directly, so a run needs no npm install and no network.

import { readFileSync, writeFileSync, mkdirSync, existsSync, rmSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));

const CHROME_CANDIDATES = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
];

function findChrome() {
  if (process.env.CHROME && existsSync(process.env.CHROME)) return process.env.CHROME;
  for (const c of CHROME_CANDIDATES) if (existsSync(c)) return c;
  throw new Error("No Chrome or Edge found. Set CHROME to a browser binary.");
}

const [specPath, outDirArg] = process.argv.slice(2);
if (!specPath) {
  console.error("usage: node visoals/render.mjs <deck.json> [outDir]".replace("visoals", "visuals"));
  process.exit(1);
}

const deck = JSON.parse(readFileSync(specPath, "utf8"));
const slides = deck.slides || [];
if (!slides.length) {
  console.error("Deck has no slides.");
  process.exit(1);
}

const outDir = resolve(outDirArg || deck.outDir || "out");
mkdirSync(outDir, { recursive: true });

const chrome = findChrome();
const specJs = join(HERE, "spec.js");
const template = join(HERE, "slide.html");
const slug = deck.slug || "deck";

// One seed for the whole deck so the starfield is consistent slide to slide, but
// offset per slide so they aren't identical backgrounds.
const baseSeed = deck.seed ?? 20260730;

const written = [];
for (let i = 0; i < slides.length; i++) {
  const slide = {
    ...slides[i],
    seed: baseSeed + i * 977,
    // last slide gets no swipe cue; a CTA never gets one
    swipe: slides[i].swipe ?? (i < slides.length - 1),
    footer: slides[i].footer ?? (i === 0 ? deck.footer : undefined),
  };

  writeFileSync(specJs, `window.SPEC = ${JSON.stringify(slide, null, 2)};\n`, "utf8");

  const out = join(outDir, `${slug}-${String(i + 1).padStart(2, "0")}.png`);
  execFileSync(chrome, [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--force-device-scale-factor=1",
    "--window-size=1080,1080",
    "--virtual-time-budget=2500",
    `--screenshot=${out}`,
    `file:///${template.replace(/\\/g, "/")}`,
  ], { stdio: ["ignore", "ignore", "ignore"] });

  if (!existsSync(out)) throw new Error(`Slide ${i + 1} produced no output`);
  written.push(out);
  console.log(`  ${String(i + 1).padStart(2, "0")}  ${slide.type.padEnd(8)}  ${out}`);
}

// leave no stale spec behind that a later manual render would silently pick up
rmSync(specJs, { force: true });

console.log(`\n${written.length} slide${written.length === 1 ? "" : "s"} -> ${outDir}`);
