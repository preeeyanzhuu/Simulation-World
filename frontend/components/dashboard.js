let rewardCtx = null;
let rewardCanvas = null;

const $ = (id) => document.getElementById(id);

export function init() {
  rewardCanvas = $("rewardChart");
  rewardCtx = rewardCanvas ? rewardCanvas.getContext("2d") : null;
}

export function update(state) {
  $("statPopulation").textContent = state.stats.population;
  $("statHappiness").textContent = `${state.stats.happiness}%`;
  $("statAtWork").textContent = `${state.stats.atWorkPct}%`;
  $("statInSchool").textContent = state.stats.inSchool;

  drawRewardChart(state.rewardHistory);
}

function drawRewardChart(history) {
  if (!rewardCtx || !history || history.length < 2) return;

  const rect = rewardCanvas.getBoundingClientRect();
  const dpr = window.devicePixelRatio || 1;
  const w = Math.round(rect.width * dpr);
  const h = Math.round(rect.height * dpr);
  if (rewardCanvas.width !== w || rewardCanvas.height !== h) {
    rewardCanvas.width = w;
    rewardCanvas.height = h;
  }
  rewardCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const { width, height } = rect;
  rewardCtx.clearRect(0, 0, width, height);

  const min = Math.min(...history);
  const max = Math.max(...history);
  const range = max - min || 1;
  const yOf = (v) => height - ((v - min) / range) * (height - 4) - 2;

  if (min < 0 && max > 0) {                   
    rewardCtx.strokeStyle = "rgba(124, 132, 148, 0.4)";
    rewardCtx.setLineDash([3, 3]);
    rewardCtx.beginPath();
    rewardCtx.moveTo(0, yOf(0));
    rewardCtx.lineTo(width, yOf(0));
    rewardCtx.stroke();
    rewardCtx.setLineDash([]);
  }

  rewardCtx.beginPath();
  rewardCtx.strokeStyle = "#E8A33D";
  rewardCtx.lineWidth = 1.5;
  history.forEach((value, index) => {
    const x = (index / (history.length - 1)) * width;
    if (index === 0) rewardCtx.moveTo(x, yOf(value));
    else rewardCtx.lineTo(x, yOf(value));
  });
  rewardCtx.stroke();
}
