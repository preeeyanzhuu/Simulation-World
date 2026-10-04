const HOST = window.location.hostname || "localhost";
const WS_URL = window.SIM_WS_URL || `ws://${HOST}:8000/ws`;
const API_BASE = window.SIM_API_BASE || `http://${HOST}:8000`;

const DEFAULT_ROAD_ID = "middle_road";
let cachedLayout = {
  buildings: [],
  roads: [],
  intersections: [],
  gridSize: 30,
  layoutVersion: -1,
};

function isNear(agent, b) {
  return agent.x >= b.gx - 1 && agent.x <= b.gx + b.w &&
         agent.y >= b.gy - 1 && agent.y <= b.gy + b.h;
}

function transform(raw) {
  if (raw.buildings && raw.buildings.length) {
    cachedLayout.buildings = raw.buildings.map((b) => ({
      type: b.building_type,
      gx: b.location[1],
      gy: b.location[0],
      w: b.width,
      h: b.height,
    }));
  }
  if (raw.roads) {
    cachedLayout.roads = (raw.roads || []).map((r) => ({
      id: r.road_id,
      cells: r.cells.map(([row, col]) => ({ x: col, y: row })),
    }));
  }
  if (raw.intersections) {
    cachedLayout.intersections = (raw.intersections || []).map(([row, col]) => ({
      x: col, y: row,
    }));
  }
  if (raw.grid_size) {
    cachedLayout.gridSize = raw.grid_size;
  }
  if (raw.layoutVersion != null) {
    cachedLayout.layoutVersion = raw.layoutVersion;
  }

  const agents = raw.agents || [];
  const buildings = cachedLayout.buildings;
  const roads = cachedLayout.roads;
  const intersections = cachedLayout.intersections;

  const alive = agents.filter((a) => a.is_alive !== false);
  const total = alive.length || 1;
  const avgHappiness = alive.reduce((sum, a) => sum + (Number(a.happiness) || 0), 0) / total;

  const students = alive.filter((a) => a.occupation === "student");
  const workers = alive.filter((a) => a.occupation !== "student");
  const schools = buildings.filter((b) => b.type === "school");
  const inSchool = students.filter((a) => schools.some((b) => isNear(a, b))).length;
  const atWork = workers.filter((a) =>
    buildings.some((b) => b.type === a.workplace && isNear(a, b))
  ).length;

  return {
    day: raw.day,
    hour: raw.hour,
    timePeriod: raw.timePeriod,
    weather: raw.weather,
    taxActive: raw.taxActive,
    roadClosureActive: raw.roadClosureActive,
    closedRoadIds: raw.closedRoadIds || [],
    running: raw.running !== false,
    streetLightsOn: !!raw.streetLightsOn,
    agents,
    buildings,
    roads,
    intersections,
    gridSize: cachedLayout.gridSize,
    rewardHistory: raw.rewardHistory,
    stats: {
      population: alive.length,
      totalCitizens: agents.length,
      happiness: Math.round(avgHappiness),
      atWorkPct: workers.length ? Math.round((atWork / workers.length) * 100) : 0,
      inSchool,
    },
  };
}
export function connect(onMessage, onStatus = () => {}) {
  let ws = null;
  let retryMs = 1000;
  let stopped = false;

  const open = () => {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      retryMs = 1000;
      cachedLayout.layoutVersion = -1;
      onStatus("connected");
    };

    ws.onmessage = (event) => {
      let state;
      try {
        state = transform(JSON.parse(event.data));
      } catch (err) {
        console.error("Simulation WebSocket: bad payload", err);
        return;
      }
      onMessage(state);
    };

    ws.onerror = (err) => console.error("Simulation WebSocket error:", err);

    ws.onclose = () => {
      onStatus("disconnected");
      if (stopped) return;
      setTimeout(open, retryMs);
      retryMs = Math.min(retryMs * 2, 8000);
    };
  };

  open();
  return () => {
    stopped = true;
    ws && ws.close();
  };
}

async function post(path, body = {}) {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) console.error(`${path} -> HTTP ${res.status}`);
  } catch (err) {
    console.error(`Request ${path} failed:`, err);
  }
}

export function send(eventName, options = {}) {
  switch (eventName) {
    case "rain":         return post("/events/rain");
    case "tax_hike":     return post("/events/tax-hike");
    case "road_closure": return post("/events/road-closure", { road_id: options.roadId || DEFAULT_ROAD_ID });
    case "sim_start":    return post("/simulation/start");
    case "sim_stop":     return post("/simulation/stop");
    case "sim_reset":    return post("/simulation/reset");
  }
}
