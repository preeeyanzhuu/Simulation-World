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

function ensureCanvasSized() {
  const rect = canvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { width: rect.width, height: rect.height };
}

export function init() {
  canvas = document.getElementById("townCanvas");
  ctx = canvas.getContext("2d");
  requestAnimationFrame(loop);
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
  const { width, height } = ensureCanvasSized();
  const cell = Math.min(width, height) / state.gridSize;

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

  ctx.font = "10px 'IBM Plex Mono', monospace";
  for (const b of state.buildings) {
    const x = b.gx * cell;
    const y = b.gy * cell;
    const size = cell * 2;
    ctx.fillStyle = BUILDING_COLORS[b.type] || "#7C8494";
    ctx.globalAlpha = 0.35;
    ctx.fillRect(x, y, size, size);
    ctx.globalAlpha = 1;
    ctx.strokeStyle = BUILDING_COLORS[b.type] || "#7C8494";
    ctx.strokeRect(x, y, size, size);
    ctx.fillStyle = "#E4E7EC";
    ctx.fillText(b.type, x + 4, y + size / 2);
  }

  if (state.roadClosureActive) {
    ctx.fillStyle = "rgba(217, 84, 79, 0.15)";
    ctx.fillRect(0, 0, width, height);
  }
  if (state.weather === "Rain") {
    ctx.fillStyle = "rgba(79, 163, 209, 0.06)";
    ctx.fillRect(0, 0, width, height);
  }

  for (const a of state.agents) {
    const p = renderPositions.get(a.id);
    const cx = (p.x + 0.5 + p.ox) * cell;
    const cy = (p.y + 0.5 + p.oy) * cell;
    const r = Math.max(1.5, cell * 0.18 * p.scale);

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    if (a.type === "learning") {
      ctx.fillStyle = "#E8A33D";
      ctx.shadowColor = "rgba(232, 163, 61, 0.6)";
      ctx.shadowBlur = 4;
    } else {
      ctx.fillStyle = "#4FA3D1";
      ctx.shadowBlur = 0;
    }
    ctx.fill();
    ctx.shadowBlur = 0;
  }
}
