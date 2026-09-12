
// services/socket.js
//
// Owns the connection to the simulation backend. Right now there IS no
// real backend (Aditya's tick loop / WebSocket don't exist yet), so this
// runs a small fake world generator on a timer instead -- same message
// shape a real WebSocket would deliver, so swapping it in later only
// means changing what's inside connect()/send(), not any other file.
//
// ===========================================================================
// SWAP POINT: once Aditya's WebSocket exists, replace the body of
// connect() and send() below with a real `new WebSocket(url)` --
// everything in app.js / townMap.js / dashboard.js / navbar.js /
// eventButtons.js stays exactly the same, since they only depend on
// the onMessage(state) shape, not on how state arrives.
// ===========================================================================

const GRID_SIZE = 20;
const TICK_MS = 400;
const DEFAULT_EVENT_DURATION_TICKS = 20;

const BUILDINGS = [
  { type: "hospital",   gx: 2,  gy: 2 },
  { type: "school",     gx: 15, gy: 2 },
  { type: "restaurant", gx: 2,  gy: 15 },
  { type: "office",     gx: 15, gy: 15 },
  { type: "mall",       gx: 9,  gy: 9 },
];

function randomAgents(count) {
  const agents = [];
  for (let i = 0; i < count; i++) {
    agents.push({
      id: `c${i}`,
      x: Math.floor(Math.random() * GRID_SIZE),
      y: Math.floor(Math.random() * GRID_SIZE),
      type: i < 10 ? "learning" : "normal",   // matches ~8-10 learning agents from the project spec
    });
  }
  return agents;
}

function stepAgents(agents) {
  for (const a of agents) {
    a.x = Math.max(0, Math.min(GRID_SIZE - 1, a.x + (Math.floor(Math.random() * 3) - 1)));
    a.y = Math.max(0, Math.min(GRID_SIZE - 1, a.y + (Math.floor(Math.random() * 3) - 1)));
  }
}

function timePeriod(hour) {
  if (hour >= 5 && hour < 12) return "morning";
  if (hour >= 12 && hour < 18) return "afternoon";
  return "evening";
}

// module-level mock world -- lets send() reach in and trigger events
// on the same state connect()'s timer is advancing
const world = {
  tick: 0,
  day: 1,
  hour: 6,
  weather: "Sunny",
  weatherTicksRemaining: 0,
  taxActive: false,
  taxTicksRemaining: 0,
  roadClosureActive: false,
  roadClosureTicksRemaining: 0,
  agents: randomAgents(58),
};

const rewardHistory = [];

export function connect(onMessage) {
  const timer = setInterval(() => {
    world.tick += 1;
    if (world.tick % 10 === 0) {
      world.hour = (world.hour + 1) % 24;
      if (world.hour === 0) world.day += 1;
    }

    if (world.weatherTicksRemaining > 0) {
      world.weatherTicksRemaining -= 1;
      if (world.weatherTicksRemaining === 0) world.weather = "Sunny";
    }
    if (world.taxTicksRemaining > 0) {
      world.taxTicksRemaining -= 1;
      if (world.taxTicksRemaining === 0) world.taxActive = false;
    }
    if (world.roadClosureTicksRemaining > 0) {
      world.roadClosureTicksRemaining -= 1;
      if (world.roadClosureTicksRemaining === 0) world.roadClosureActive = false;
    }

    stepAgents(world.agents);

    const avgReward = 5 + Math.sin(world.tick / 20) * 2 + (Math.random() - 0.5);
    rewardHistory.push(avgReward);
    if (rewardHistory.length > 60) rewardHistory.shift();

    const learningCount = world.agents.filter(a => a.type === "learning").length;

    onMessage({
      day: world.day,
      hour: world.hour,
      timePeriod: timePeriod(world.hour),
      weather: world.weather,
      taxActive: world.taxActive,
      roadClosureActive: world.roadClosureActive,
      agents: world.agents,
      buildings: BUILDINGS,
      gridSize: GRID_SIZE,
      rewardHistory,
      stats: {
        population: world.agents.length,
        happiness: Math.round(60 + Math.sin(world.tick / 15) * 15),
        employedPct: Math.round(75 + Math.cos(world.tick / 25) * 10),
        inSchool: learningCount,
      },
    });
  }, TICK_MS);

  return () => clearInterval(timer);   // returns a disconnect function

  // --- what a real connection will look like, for reference ---
  // const ws = new WebSocket("ws://localhost:8000/ws/simulation");
  // ws.onmessage = (event) => onMessage(JSON.parse(event.data));
  // return () => ws.close();
}

export function send(eventName) {
  // MOCK: mutate the local fake world directly since there's no real
  // backend yet. Real version: ws.send(JSON.stringify({ event: eventName }));
  if (eventName === "rain") {
    world.weather = "Rain";
    world.weatherTicksRemaining = DEFAULT_EVENT_DURATION_TICKS;
  } else if (eventName === "tax_hike") {
    world.taxActive = true;
    world.taxTicksRemaining = DEFAULT_EVENT_DURATION_TICKS;
  } else if (eventName === "road_closure") {
    world.roadClosureActive = true;
    world.roadClosureTicksRemaining = DEFAULT_EVENT_DURATION_TICKS;
  }
}
