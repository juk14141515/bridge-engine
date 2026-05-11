import { spawn } from "node:child_process";

const PORT = 8791;
const base = `http://localhost:${PORT}`;
const child = spawn(process.execPath, ["server/index.mjs"], {
  env: { ...process.env, PORT: String(PORT), BRIDGE_AUTH_SECRET: "smoke-test-secret" },
  stdio: ["ignore", "ignore", "inherit"],
});

try {
  await waitForServer();
  const email = `test-${Date.now()}@bridge.local`;
  const auth = await post("/api/auth/signup", { email, password: "password1" });
  assert(auth.token, "signup returns token");

  const headers = { Authorization: `Bearer ${auth.token}` };
  const me = await get("/api/me", headers);
  assert(me.user.email === email, "me returns user");

  await post("/api/intake", { startingFeelsHeavierThanDoing: true, learningStyle: ["visual"] }, headers);
  const intake = await get("/api/intake", headers);
  assert(intake.intake.startingFeelsHeavierThanDoing, "intake saved");

  await post("/api/entry-memory", {
    frictionChoice: "overwhelm",
    attentionPathway: "systems",
    tinyAction: "Pick one corner.",
    outcome: "lighter",
  }, headers);
  const memory = await get("/api/entry-memory", headers);
  assert(memory.entries.length === 1, "entry memory saved");

  const plan = await post("/api/bridge-plan", { stuckText: "too much at once", pathway: "systems" });
  assert(plan.plan.tinyAction, "bridge plan returned");

  const help = await post("/api/adaptive-help", { helpMode: "smaller", pathway: "systems", entryMemory: memory.entries });
  assert(help.help.instruction, "adaptive help returned");

  const gaming = await post("/api/bridge-plan", { stuckText: "too much at once", pathway: "gaming" });
  const systems = await post("/api/bridge-plan", { stuckText: "too much at once", pathway: "systems" });
  assert(gaming.plan.relevanceMapping !== systems.plan.relevanceMapping, "gaming and systems frame differently");
  assert(gaming.plan.tinyAction !== systems.plan.tinyAction, "gaming and systems tiny actions differ");

  const smaller1 = await post("/api/adaptive-help", { helpMode: "smaller", smallerLevel: 1, pathway: "systems", entryMemory: [] });
  const smaller2 = await post("/api/adaptive-help", { helpMode: "smaller", smallerLevel: 2, pathway: "systems", entryMemory: [] });
  const smaller3 = await post("/api/adaptive-help", { helpMode: "smaller", smallerLevel: 3, pathway: "systems", entryMemory: [] });
  assert(smaller1.help.instruction !== smaller2.help.instruction, "smaller levels 1 and 2 differ");
  assert(smaller2.help.instruction !== smaller3.help.instruction, "smaller levels 2 and 3 differ");

  const cont1 = await post("/api/adaptive-help", { helpMode: "continue", continuationLevel: 1, pathway: "systems", entryMemory: [] });
  const cont2 = await post("/api/adaptive-help", { helpMode: "continue", continuationLevel: 2, pathway: "systems", entryMemory: [] });
  assert(cont1.help.instruction !== cont2.help.instruction, "continue does not repeat");

  const another1 = await post("/api/adaptive-help", { helpMode: "another", anotherIndex: 1, pathway: "gaming", entryMemory: [] });
  const another2 = await post("/api/adaptive-help", { helpMode: "another", anotherIndex: 2, pathway: "gaming", entryMemory: [] });
  assert(another1.help.instruction !== another2.help.instruction, "another way rotates");

  const lowFuel = await post("/api/adaptive-help", {
    helpMode: "continue",
    pathway: "systems",
    supportPreferences: { lowFuel: true },
    entryMemory: [],
  });
  assert(lowFuel.help.headline === "No task yet.", "low fuel returns lower-demand help");

  await post("/api/bridge-feedback", {
    frictionType: "overwhelm",
    pathway: "gaming",
    helpMode: "smaller",
    bridgeText: "x",
    tinyAction: "y",
    feedback: "helped",
    timestamp: Date.now(),
  }, headers);
  const profileAfterHelped = await get("/api/adaptive-profile", headers);
  assert(profileAfterHelped.adaptiveProfile.memoryProfile.preferredPathways.includes("gaming"), "helped changes adaptive profile");

  await post("/api/bridge-feedback", {
    frictionType: "overwhelm",
    pathway: "systems",
    helpMode: "continue",
    bridgeText: "x",
    tinyAction: "y",
    feedback: "too_much",
    timestamp: Date.now(),
  }, headers);
  await post("/api/bridge-feedback", {
    frictionType: "overwhelm",
    pathway: "systems",
    helpMode: "continue",
    bridgeText: "x",
    tinyAction: "y",
    feedback: "too_much",
    timestamp: Date.now(),
  }, headers);
  const afterTooMuch = await post("/api/adaptive-help", { helpMode: "continue", pathway: "systems" }, headers);
  assert(afterTooMuch.help.headline === "Smaller works.", "too_much makes next help smaller");

  await post("/api/bridge-feedback", {
    frictionType: "overwhelm",
    pathway: "gaming",
    helpMode: "another",
    bridgeText: "x",
    tinyAction: "y",
    feedback: "different_angle",
    timestamp: Date.now(),
  }, headers);
  await post("/api/bridge-feedback", {
    frictionType: "overwhelm",
    pathway: "gaming",
    helpMode: "another",
    bridgeText: "x",
    tinyAction: "y",
    feedback: "different_angle",
    timestamp: Date.now(),
  }, headers);
  const rotated = await post("/api/adaptive-help", { helpMode: "another", pathway: "gaming", anotherIndex: 1 }, headers);
  assert(rotated.help.instruction !== another1.help.instruction, "different_angle rotates output sooner");

  const investing = await post("/api/bridge-plan", { stuckText: "too much at once", pathway: "investing" });
  assert(gaming.plan.relevanceMapping !== investing.plan.relevanceMapping, "gaming and investing framing differs");

  const secondAuth = await post("/api/auth/signup", { email: `test-2-${Date.now()}@bridge.local`, password: "password1" });
  const secondMemory = await get("/api/entry-memory", { Authorization: `Bearer ${secondAuth.token}` });
  assert(secondMemory.entries.length === 0, "logged-in memory is user-specific");

  console.log("API smoke test passed");
} finally {
  child.kill();
}

async function waitForServer() {
  for (let i = 0; i < 40; i += 1) {
    try {
      await fetch(`${base}/api/bridge-plan`, { method: "POST", body: "{}", headers: { "Content-Type": "application/json" } });
      return;
    } catch {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }
  throw new Error("Server did not start");
}

async function get(path, headers = {}) {
  const res = await fetch(`${base}${path}`, { headers });
  if (!res.ok) throw new Error(`${path} failed: ${res.status}`);
  return res.json();
}

async function post(path, body, headers = {}) {
  const res = await fetch(`${base}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`${path} failed: ${res.status} ${await res.text()}`);
  return res.json();
}

function assert(value, message) {
  if (!value) throw new Error(message);
}

