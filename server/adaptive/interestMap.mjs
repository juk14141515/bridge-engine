const maps = {
  gaming: {
    frame: "This is a level-entry problem. Do not beat the level yet — find the first objective.",
    tiny: "Open the material and find the first objective.",
    continue: "Do the next move only. No full level.",
    another: ["Look for the easiest unlock.", "Find the first mechanic.", "Treat this as scouting the map."],
  },
  systems: {
    frame: "Treat it like a system: one input, one rule, one moving part.",
    tiny: "Identify the first moving part.",
    continue: "Touch the next subsystem only.",
    another: ["Find the input.", "Name the rule.", "Trace one small cause and effect."],
  },
  movement: {
    frame: "Start body-first. Motion can come before clarity.",
    tiny: "Stand, open it, touch one thing.",
    continue: "Move your body first, then do the next touch.",
    another: ["Change posture.", "Put it in front of you.", "Use one physical action."],
  },
  music: {
    frame: "Find the rhythm. Make one repeatable beat.",
    tiny: "Create one repeatable beat.",
    continue: "Repeat the beat once more.",
    another: ["Lower the tempo.", "Find the first rhythm.", "Hum the shape before doing it."],
  },
  investing: {
    frame: "This is signal-finding, not finishing. Look for one useful signal.",
    tiny: "Find one thing that tells you what matters first.",
    continue: "Check the next signal only.",
    another: ["Reduce the risk.", "Find the cleanest data point.", "Ask what would improve the decision."],
  },
  coding: {
    frame: "This is a debugging entry. Find the first failing point.",
    tiny: "Open the place it lives and locate the first error or unknown.",
    continue: "Inspect the next state only.",
    another: ["Find the failing case.", "Open the smallest file.", "Trace one value."],
  },
  logic: {
    frame: "Make the edge visible. One premise at a time.",
    tiny: "Find the first edge.",
    continue: "Follow one next step.",
    another: ["Remove one assumption.", "Choose the simplest rule.", "Point at what is known."],
  },
  visual: {
    frame: "See it first. Enter through shape, not explanation.",
    tiny: "Look for the first visible edge.",
    continue: "Mark or point at the next visible piece.",
    another: ["Make it visible.", "Move it where you can see it.", "Circle one corner mentally."],
  },
  fitness: {
    frame: "This is warm-up logic. No max effort yet.",
    tiny: "Do the smallest warm-up version for 30 seconds.",
    continue: "Repeat the warm-up once.",
    another: ["Lower the weight.", "Start with range of motion.", "Do the first rep only."],
  },
  entrepreneurship: {
    frame: "This is leverage-finding. Find the first useful signal or person.",
    tiny: "Name the first person, offer, or next question.",
    continue: "Move one conversation forward.",
    another: ["Find the smallest ask.", "Clarify one offer.", "Choose one useful signal."],
  },
  creativity: {
    frame: "This is making, not judging. Create the first mark.",
    tiny: "Make one rough mark or fragment.",
    continue: "Add one more rough piece.",
    another: ["Change medium.", "Copy one tiny shape.", "Make the bad version first."],
  },
};

export function pathwayMap(pathway = "systems") {
  return maps[pathway] ?? maps.systems;
}

export function rotatePathwayApproach(pathway, index = 0) {
  const map = pathwayMap(pathway);
  return map.another[Math.max(0, index - 1) % map.another.length];
}

