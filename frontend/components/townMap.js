

const BUILDING_COLORS = {
  hospital: "#4FA3D1",
  school: "#4FA3D1",
  restaurant: "#8A6427",
  office: "#7C8494",
  mall: "#8A6427",
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


export function setState(state) {
  latestState = state;
  for (const a of state.agents) {
    if (!renderPositions.has(a.id)) {
      renderPositions.set(a.id, { x: a.x, y: a.y });
    }
  }
}

function loop() {
  if (latestState) {
    for (const a of latestState.agents) {
      const p = renderPositions.get(a.id);
      p.x += (a.x - p.x) * LERP_FACTOR;
      p.y += (a.y - p.y) * LERP_FACTOR;
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
    const cx = p.x * cell + cell / 2;
    const cy = p.y * cell + cell / 2;
    const r = Math.max(2, cell * 0.18);

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
