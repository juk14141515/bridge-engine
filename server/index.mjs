import { createServer } from "node:http";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createHmac, pbkdf2Sync, randomBytes, timingSafeEqual } from "node:crypto";
import {
  createAdaptiveHelp as createEngineAdaptiveHelp,
  createAdaptiveProfile,
  createBridgePlan as createEngineBridgePlan,
} from "./adaptive/bridgeEngine.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DB_PATH = join(__dirname, "data", "db.json");
const PORT = Number(process.env.PORT ?? 8787);
const SECRET = process.env.BRIDGE_AUTH_SECRET ?? "bridge-engine-dev-secret";

ensureDb();

const server = createServer(async (req, res) => {
  setCors(res);
  if (req.method === "OPTIONS") return send(res, 204, null);

  try {
    const url = new URL(req.url ?? "/", `http://${req.headers.host}`);
    const path = url.pathname;

    if (req.method === "POST" && path === "/api/auth/signup") return signup(req, res);
    if (req.method === "POST" && path === "/api/auth/login") return login(req, res);
    if (req.method === "GET" && path === "/api/me") return me(req, res);

    if (req.method === "GET" && path === "/api/intake") return getIntake(req, res);
    if (req.method === "POST" && path === "/api/intake") return saveIntake(req, res);

    if (req.method === "GET" && path === "/api/entry-memory") return getEntryMemory(req, res);
    if (req.method === "POST" && path === "/api/entry-memory") return saveEntryMemory(req, res);
    if (req.method === "POST" && path === "/api/bridge-outcome") return bridgeOutcome(req, res);
    if (req.method === "POST" && path === "/api/bridge-feedback") return bridgeFeedback(req, res);

    if (req.method === "POST" && path === "/api/bridge-plan") return bridgePlan(req, res);
    if (req.method === "POST" && path === "/api/adaptive-help") return adaptiveHelp(req, res);
    if (req.method === "GET" && path === "/api/adaptive-profile") return adaptiveProfile(req, res);

    return send(res, 404, { error: "Not found" });
  } catch (error) {
    return send(res, 500, { error: error instanceof Error ? error.message : "Server error" });
  }
});

server.listen(PORT, () => {
  console.log(`Bridge API listening on http://localhost:${PORT}`);
});

async function signup(req, res) {
  const body = await readJson(req);
  const email = cleanEmail(body.email);
  const password = String(body.password ?? "");
  if (!email || password.length < 6) return send(res, 400, { error: "Email and 6+ character password required" });

  const db = readDb();
  if (db.users.some((user) => user.email === email)) return send(res, 409, { error: "Account already exists" });

  const user = {
    id: id("user"),
    email,
    passwordHash: hashPassword(password),
    createdAt: Date.now(),
  };
  db.users.push(user);
  db.intake[user.id] = defaultIntake();
  db.entryMemory[user.id] = [];
  db.feedback[user.id] = [];
  writeDb(db);

  return send(res, 201, authPayload(user));
}

async function login(req, res) {
  const body = await readJson(req);
  const email = cleanEmail(body.email);
  const password = String(body.password ?? "");
  const db = readDb();
  const user = db.users.find((u) => u.email === email);

  if (!user || !verifyPassword(password, user.passwordHash)) return send(res, 401, { error: "Invalid login" });
  return send(res, 200, authPayload(user));
}

function me(req, res) {
  const user = requireUser(req, res);
  if (!user) return;
  return send(res, 200, { user: publicUser(user) });
}

function getIntake(req, res) {
  const user = requireUser(req, res);
  if (!user) return;
  const db = readDb();
  return send(res, 200, { intake: db.intake[user.id] ?? defaultIntake() });
}

async function saveIntake(req, res) {
  const user = requireUser(req, res);
  if (!user) return;
  const body = await readJson(req);
  const db = readDb();
  db.intake[user.id] = normalizeIntake(body.intake ?? body);
  writeDb(db);
  return send(res, 200, { intake: db.intake[user.id] });
}

function getEntryMemory(req, res) {
  const user = requireUser(req, res);
  if (!user) return;
  const db = readDb();
  return send(res, 200, { entries: db.entryMemory[user.id] ?? [] });
}

async function saveEntryMemory(req, res) {
  const user = requireUser(req, res);
  if (!user) return;
  const body = await readJson(req);
  const db = readDb();
  const entry = normalizeEntry(body.entry ?? body);
  db.entryMemory[user.id] = [entry, ...(db.entryMemory[user.id] ?? [])].slice(0, 100);
  writeDb(db);
  return send(res, 201, { entry, entries: db.entryMemory[user.id] });
}

async function bridgeOutcome(req, res) {
  const user = requireUser(req, res);
  if (!user) return;
  const body = await readJson(req);
  const db = readDb();
  const entry = normalizeEntry({ ...(body.entry ?? body), outcome: body.outcome ?? body.entry?.outcome });
  db.entryMemory[user.id] = [entry, ...(db.entryMemory[user.id] ?? [])].slice(0, 100);
  writeDb(db);
  return send(res, 201, { entry, entries: db.entryMemory[user.id] });
}

async function bridgePlan(req, res) {
  const body = await readJson(req);
  const user = optionalUser(req);
  const db = readDb();
  const entryMemory = user ? db.entryMemory[user.id] ?? [] : body.entryMemory ?? [];
  const feedback = user ? db.feedback[user.id] ?? [] : body.feedback ?? [];
  const supportPreferences = body.supportPreferences ?? (user ? db.intake[user.id] ?? defaultIntake() : {});
  return send(res, 200, { plan: createEngineBridgePlan({ ...body, entryMemory, feedback, supportPreferences }) });
}

async function adaptiveHelp(req, res) {
  const body = await readJson(req);
  const user = optionalUser(req);
  const db = readDb();
  const entryMemory = user ? db.entryMemory[user.id] ?? [] : body.entryMemory ?? [];
  const feedback = user ? db.feedback[user.id] ?? [] : body.feedback ?? [];
  const supportPreferences = body.supportPreferences ?? (user ? db.intake[user.id] ?? defaultIntake() : {});
  return send(res, 200, { help: createEngineAdaptiveHelp({ ...body, entryMemory, feedback, supportPreferences }) });
}

function adaptiveProfile(req, res) {
  const user = requireUser(req, res);
  if (!user) return;
  const db = readDb();
  return send(res, 200, {
    adaptiveProfile: createAdaptiveProfile({
      intake: db.intake[user.id] ?? defaultIntake(),
      entryMemory: db.entryMemory[user.id] ?? [],
      feedback: db.feedback[user.id] ?? [],
    }),
  });
}

async function bridgeFeedback(req, res) {
  const body = await readJson(req);
  const user = optionalUser(req);
  const feedback = normalizeFeedback(body);

  if (!user) return send(res, 201, { feedback });

  const db = readDb();
  db.feedback[user.id] = [feedback, ...(db.feedback[user.id] ?? [])].slice(0, 200);
  writeDb(db);
  return send(res, 201, {
    feedback,
    adaptiveProfile: createAdaptiveProfile({
      intake: db.intake[user.id] ?? defaultIntake(),
      entryMemory: db.entryMemory[user.id] ?? [],
      feedback: db.feedback[user.id] ?? [],
    }),
  });
}

function requireUser(req, res) {
  const token = (req.headers.authorization ?? "").replace(/^Bearer\s+/i, "");
  const userId = verifyToken(token);
  const user = userId ? readDb().users.find((u) => u.id === userId) : null;
  if (!user) {
    send(res, 401, { error: "Login required" });
    return null;
  }
  return user;
}

function optionalUser(req) {
  const token = (req.headers.authorization ?? "").replace(/^Bearer\s+/i, "");
  const userId = verifyToken(token);
  return userId ? readDb().users.find((u) => u.id === userId) ?? null : null;
}

function authPayload(user) {
  return { token: signToken(user.id), user: publicUser(user) };
}

function publicUser(user) {
  return { id: user.id, email: user.email, createdAt: user.createdAt };
}

function defaultIntake() {
  return {
    startingFeelsHeavierThanDoing: false,
    tooManyOptionsShutMeDown: false,
    brainJumpsTracks: false,
    readingIsTiring: false,
    taskFeelsEmotionallyHeavy: false,
    lowFuelSupport: false,
    dyslexiaFriendlyReadability: false,
    adhdStyleFrictionSupport: false,
    depressionLowEnergySupport: false,
    learningStyle: [],
  };
}

function normalizeIntake(input) {
  const defaults = defaultIntake();
  return {
    startingFeelsHeavierThanDoing: Boolean(input.startingFeelsHeavierThanDoing),
    tooManyOptionsShutMeDown: Boolean(input.tooManyOptionsShutMeDown),
    brainJumpsTracks: Boolean(input.brainJumpsTracks),
    readingIsTiring: Boolean(input.readingIsTiring),
    taskFeelsEmotionallyHeavy: Boolean(input.taskFeelsEmotionallyHeavy),
    lowFuelSupport: Boolean(input.lowFuelSupport),
    dyslexiaFriendlyReadability: Boolean(input.dyslexiaFriendlyReadability),
    adhdStyleFrictionSupport: Boolean(input.adhdStyleFrictionSupport),
    depressionLowEnergySupport: Boolean(input.depressionLowEnergySupport),
    learningStyle: Array.isArray(input.learningStyle) ? input.learningStyle.slice(0, 6).map(String) : defaults.learningStyle,
  };
}

function normalizeEntry(input) {
  return {
    id: String(input.id ?? id("entry")),
    createdAt: Number(input.createdAt ?? Date.now()),
    frictionChoice: String(input.frictionChoice ?? "starting"),
    frictionType: String(input.frictionType ?? input.frictionChoice ?? "starting"),
    attentionPathway: String(input.attentionPathway ?? "systems"),
    pathway: String(input.pathway ?? input.attentionPathway ?? "systems"),
    tinyAction: String(input.tinyAction ?? "Open the place it lives."),
    helpMode: String(input.helpMode ?? "unknown"),
    continuationLevel: Number(input.continuationLevel ?? 0),
    smallerLevel: Number(input.smallerLevel ?? 0),
    outcome: ["lighter", "smaller", "another"].includes(input.outcome) ? input.outcome : "lighter",
  };
}

function normalizeFeedback(input) {
  const allowed = ["helped", "not_quite", "too_much", "different_angle"];
  return {
    id: String(input.id ?? id("feedback")),
    entryId: input.entryId ? String(input.entryId) : undefined,
    frictionType: String(input.frictionType ?? "ambiguity"),
    pathway: String(input.pathway ?? "systems"),
    helpMode: String(input.helpMode ?? "bridge"),
    bridgeText: String(input.bridgeText ?? ""),
    tinyAction: String(input.tinyAction ?? ""),
    feedback: allowed.includes(input.feedback) ? input.feedback : "not_quite",
    timestamp: Number(input.timestamp ?? Date.now()),
  };
}

function signToken(userId) {
  const payload = Buffer.from(JSON.stringify({ userId, exp: Date.now() + 1000 * 60 * 60 * 24 * 30 })).toString("base64url");
  const sig = createHmac("sha256", SECRET).update(payload).digest("base64url");
  return `${payload}.${sig}`;
}

function verifyToken(token) {
  const [payload, sig] = token.split(".");
  if (!payload || !sig) return null;
  const expected = createHmac("sha256", SECRET).update(payload).digest("base64url");
  if (!safeEqual(sig, expected)) return null;
  const parsed = JSON.parse(Buffer.from(payload, "base64url").toString("utf8"));
  if (parsed.exp < Date.now()) return null;
  return parsed.userId;
}

function hashPassword(password) {
  const salt = randomBytes(16).toString("hex");
  const hash = pbkdf2Sync(password, salt, 100_000, 32, "sha256").toString("hex");
  return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
  const [salt, hash] = stored.split(":");
  const attempt = pbkdf2Sync(password, salt, 100_000, 32, "sha256").toString("hex");
  return safeEqual(attempt, hash);
}

function safeEqual(a, b) {
  const aa = Buffer.from(a);
  const bb = Buffer.from(b);
  return aa.length === bb.length && timingSafeEqual(aa, bb);
}

function cleanEmail(value) {
  return String(value ?? "").trim().toLowerCase();
}

function id(prefix) {
  return `${prefix}_${Date.now().toString(16)}_${randomBytes(6).toString("hex")}`;
}

function ensureDb() {
  mkdirSync(dirname(DB_PATH), { recursive: true });
  if (!existsSync(DB_PATH)) writeDb({ users: [], intake: {}, entryMemory: {}, feedback: {} });
  else {
    const db = readDb();
    db.feedback ??= {};
    db.entryMemory ??= {};
    db.intake ??= {};
    db.users ??= [];
    writeDb(db);
  }
}

function readDb() {
  return JSON.parse(readFileSync(DB_PATH, "utf8"));
}

function writeDb(db) {
  writeFileSync(DB_PATH, JSON.stringify(db, null, 2));
}

async function readJson(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  if (!chunks.length) return {};
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
}

function send(res, status, body) {
  res.statusCode = status;
  if (body === null) return res.end();
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(body));
}

