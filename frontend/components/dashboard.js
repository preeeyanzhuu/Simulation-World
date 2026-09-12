
// components/dashboard.js

let rewardCtx = null;
let rewardCanvas = null;

export function init() {
  rewardCanvas = document.getElementById("rewardChart");
  rewardCtx = rewardCanvas.getContext("2d");
}

export function update(state) {
  document.getElementById("statPopulation").textContent = state.stats.population;
  document.getElementById("statHappiness").textContent = `${state.stats.happiness}%`;
  document.getElementById("statEmployed").textContent = `${state.stats.employedPct}%`;
  document.getElementById("statInSchool").textContent = state.stats.inSchool;

  drawRewardChart(state.rewardHistory);
}

function drawRewardChart(history) {
  if (!rewardCtx || history.length < 2) return;

  const rect = rewardCanvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  rewardCanvas.width = rect.width * dpr;
  rewardCanvas.height = rect.height * dpr;
  rewardCtx.setTransform(dpr, 0, 0, dpr, 0, 0);

  const { width, height } = rect;
  rewardCtx.clearRect(0, 0, width, height);

  const min = Math.min(...history);
  const max = Math.max(...history);
  const range = max - min || 1;

  rewardCtx.beginPath();
  rewardCtx.strokeStyle = "#E8A33D";
  rewardCtx.lineWidth = 1.5;

  history.forEach((val, i) => {
    const x = (i / (history.length - 1)) * width;
    const y = height - ((val - min) / range) * height;
    if (i === 0) rewardCtx.moveTo(x, y);
    else rewardCtx.lineTo(x, y);
  });

  rewardCtx.stroke();
}
