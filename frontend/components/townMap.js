const BUILDING_COLORS = {
  hospital: "#4FA3D1",
  school: "#4FA3D1",
  restaurant: "#8A6427",
  office: "#7C8494",
  mall: "#8A6427",
  house: "#5C9E6F",
  park: "#3E8E5A",
};

const LERP_FACTOR = 0.12;

let ctx = null;
let canvas = null;
let latestState = null;
const renderPositions = new Map();
let lastCell = 1;                 
let selectedId = null;
const selectListeners = [];

export function getSelectedId() {
  return selectedId;
}

export function select(id) {
  if (id === selectedId) return;
  selectedId = id;
  selectListeners.forEach((fn) => fn(id));
}

export function onSelect(fn) {
  selectListeners.push(fn);
}

let cssWidth = 0;
let cssHeight = 0;
function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  cssWidth = rect.width;
  cssHeight = rect.height;
  canvas.width = Math.round(rect.width * dpr);
  canvas.height = Math.round(rect.height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
}

export function init() {
  canvas = document.getElementById("townCanvas");
  ctx = canvas.getContext("2d");
  canvas.style.cursor = "pointer";
  canvas.addEventListener("click", handleClick);
  resizeCanvas();
  new ResizeObserver(resizeCanvas).observe(canvas);
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") select(null);
  });
  requestAnimationFrame(loop);
}
function handleClick(e) {
  if (!latestState) return;
  const rect = canvas.getBoundingClientRect();
  const mx = e.clientX - rect.left;
  const my = e.clientY - rect.top;

  let best = null;
  let bestDist = Infinity;
  for (const a of latestState.agents) {
    const p = renderPositions.get(a.id);
    if (!p) continue;
    const d = Math.hypot(mx - (p.x + 0.5 + p.ox) * lastCell, my - (p.y + 0.5 + p.oy) * lastCell);
    if (d < bestDist) {
      bestDist = d;
      best = a;
    }
  }
  const reach = Math.max(10, lastCell * 0.5);
  select(best && bestDist <= reach ? best.id : null);
}
export function computeSlotOffsets(agents) {
  const groups = new Map();
  for (const a of agents) {
    const key = `${a.x},${a.y}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(a);
  }

  const DOT_DIAMETER = 0.36;
  const SPREAD = 0.8; 
  const offsets = new Map();

  for (const members of groups.values()) {
    if (members.length === 1) {
      offsets.set(members[0].id, { ox: 0, oy: 0, scale: 1 });
      continue;
    }
    members.sort((a, b) => a.id - b.id);
    const cols = Math.ceil(Math.sqrt(members.length));
    const rows = Math.ceil(members.length / cols);
    const step = SPREAD / cols;
    const scale = Math.min(1, (step * 0.9) / DOT_DIAMETER);
    members.forEach((m, i) => {
      offsets.set(m.id, {
        ox: ((i % cols) - (cols - 1) / 2) * step,
        oy: (Math.floor(i / cols) - (rows - 1) / 2) * step,
        scale,
      });
    });
  }
  return offsets;
}

export function setState(state) {
  latestState = state;
  const ids = new Set(state.agents.map((a) => a.id));
  for (const id of [...renderPositions.keys()]) {
    if (!ids.has(id)) renderPositions.delete(id);
  }
  for (const a of state.agents) {
    if (!renderPositions.has(a.id)) {
      renderPositions.set(a.id, { x: a.x, y: a.y, ox: 0, oy: 0, scale: 1 });
    }
  }
}

function loop() {
  if (latestState) {
    const slots = computeSlotOffsets(latestState.agents);
    for (const a of latestState.agents) {
      const p = renderPositions.get(a.id);
      const slot = slots.get(a.id);
      p.x += (a.x - p.x) * LERP_FACTOR;
      p.y += (a.y - p.y) * LERP_FACTOR;
      p.ox += (slot.ox - p.ox) * LERP_FACTOR;
      p.oy += (slot.oy - p.oy) * LERP_FACTOR;
      p.scale += (slot.scale - p.scale) * LERP_FACTOR;
    }
    draw(latestState);
  }
  requestAnimationFrame(loop);
}


function draw(state) {
  const width = cssWidth;
  const height = cssHeight;
  const cell = Math.min(width, height) / state.gridSize;
  lastCell = cell;

  ctx.clearRect(0, 0, width, height);

  ctx.strokeStyle = "#1A1F2B";
  ctx.lineWidth = 1;
  for (let i = 0; i <= state.gridSize; i++) {
    ctx.beginPath();
    ctx.moveTo(i * cell, 0);
    ctx.lineTo(i * cell, state.gridSize * cell);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, i * cell);
    ctx.lineTo(state.gridSize * cell, i * cell);
    ctx.stroke();
  }

  const closed = new Set(state.closedRoadIds || []);
  for (const road of state.roads || []) {
    const isClosed = closed.has(road.id);
    ctx.fillStyle = isClosed ? "rgba(217, 84, 79, 0.55)" : "#232935";
    for (const c of road.cells) {
      ctx.fillRect(c.x * cell + 1, c.y * cell + 1, cell - 2, cell - 2);
    }
  }

  ctx.font = "10px 'IBM Plex Mono', monospace";
  for (const b of state.buildings) {
    const x = b.gx * cell;
    const y = b.gy * cell;
    const bw = b.w * cell;
    const bh = b.h * cell;
    const color = BUILDING_COLORS[b.type] || "#7C8494";
    ctx.fillStyle = color;
    ctx.globalAlpha = 0.35;
    ctx.fillRect(x, y, bw, bh);
    ctx.globalAlpha = 1;
    ctx.strokeStyle = color;
    ctx.strokeRect(x, y, bw, bh);
    if (bw >= 30) {
      ctx.fillStyle = "#E4E7EC";
      ctx.fillText(b.type, x + 4, y + Math.min(bh, 20) / 2 + 4, bw - 6);
    }
  }

  if (state.streetLightsOn) {              
    ctx.fillStyle = "rgba(6, 10, 30, 0.30)";
    ctx.fillRect(0, 0, width, height);
  }
  if (state.weather === "Rain") {
    ctx.fillStyle = "rgba(79, 163, 209, 0.08)";
    ctx.fillRect(0, 0, width, height);
  }

  const sel = selectedId == null ? null : state.agents.find((a) => a.id === selectedId);
  if (sel && sel.goal) {
    const sp = renderPositions.get(sel.id);
    ctx.save();
    ctx.setLineDash([4, 4]);
    ctx.strokeStyle = "rgba(228, 231, 236, 0.5)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo((sp.x + 0.5) * cell, (sp.y + 0.5) * cell);
    ctx.lineTo((sel.goal.x + 0.5) * cell, (sel.goal.y + 0.5) * cell);
    ctx.stroke();
    ctx.restore();
    ctx.strokeStyle = "rgba(228, 231, 236, 0.8)";
    ctx.strokeRect(sel.goal.x * cell + 2, sel.goal.y * cell + 2, cell - 4, cell - 4);
  }

  for (const a of state.agents) {
    const p = renderPositions.get(a.id);
    const cx = (p.x + 0.5 + p.ox) * cell;
    const cy = (p.y + 0.5 + p.oy) * cell;
    const r = Math.max(1.5, cell * 0.18 * p.scale);

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    if (a.is_alive === false) {              
      ctx.fillStyle = "#4A5261";
      ctx.shadowBlur = 0;
    } else if (a.type === "learning") {
      ctx.fillStyle = "#E8A33D";
      ctx.shadowColor = "rgba(232, 163, 61, 0.6)";
      ctx.shadowBlur = 4;
    } else {
      ctx.fillStyle = "#4FA3D1";
      ctx.shadowBlur = 0;
    }
    ctx.fill();
    ctx.shadowBlur = 0;

    if (a.id === selectedId) {            
      ctx.beginPath();
      ctx.arc(cx, cy, r + 4, 0, Math.PI * 2);
      ctx.strokeStyle = "#E4E7EC";
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.lineWidth = 1;
    }
  }
}
