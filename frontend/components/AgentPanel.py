import * as townMap from "./Townmap.js";

const ACTION_LABELS = {
  go_home: "Heading home",
  go_restaurant: "Going to eat",
  go_mall: "Going to the mall",
  go_school: "Going to school",
  go_work: "Going to work",
  go_park: "Going to the park",
  idle: "Idle",
};
const WARN = {
  energy: (v) => v < 30,
  hunger: (v) => v > 70,
  happiness: (v) => v < 30,
};

let lastState = null;
const $ = (id) => document.getElementById(id);

const dash = (v) => (v === undefined || v === null || v === "" ? "—" : v);
const isNum = (v) => typeof v === "number" && Number.isFinite(v);
const num = (v, digits = 1) => (isNum(v) ? +v.toFixed(digits) : "—");
const cellText = (p) => (p ? `col ${p.x}, row ${p.y}` : "—");

export function init() {
  $("agentClose").addEventListener("click", () => townMap.select(null));
  townMap.onSelect(() => render());
  render();
}

export function update(state) {
  lastState = state;
  render();
}

function render() {
  const id = townMap.getSelectedId();
  const agent = id == null || !lastState ? null : lastState.agents.find((a) => a.id === id);

  if (id != null && lastState && !agent) {   
    townMap.select(null);
    return;
  }

  $("agentEmpty").hidden = agent !== null;
  $("agentBody").hidden = agent === null;
  $("agentClose").hidden = agent === null;
  if (!agent) {
    $("agentTitle").textContent = "Citizen";
    return;
  }

  $("agentTitle").textContent = dash(agent.name);
  $("agentSub").textContent =
    `#${agent.id} · ${String(agent.occupation ?? "unknown").replaceAll("_", " ")} · age ${dash(agent.age)}`;

  for (const key of ["energy", "hunger", "happiness"]) {
    const row = document.querySelector(`.bar-row[data-stat="${key}"]`);
    if (!row) continue;
    const value = agent[key];
    const ok = isNum(value);             
    row.querySelector(".bar-fill").style.width = ok ? `${Math.max(0, Math.min(100, value))}%` : "0%";
    row.querySelector(".bar-value").textContent = ok ? Math.round(value) : "—";
    row.classList.toggle("is-warn", ok && WARN[key](value));
  }

  const [step, total] = Array.isArray(agent.progress) ? agent.progress : [0, 0];

  $("factMoney").textContent = num(agent.money);
  $("factAction").textContent = ACTION_LABELS[agent.action] || dash(agent.action);
  $("factPosition").textContent = cellText(agent);
  $("factGoal").textContent = cellText(agent.goal);
  $("factProgress").textContent = total > 1 ? `${step} / ${total - 1} steps` : "—";
  $("factHome").textContent = cellText(agent.home);
  $("factWorkplace").textContent = dash(agent.workplace);
  $("factReward").textContent = num(agent.last_reward, 2);
  $("factStatus").textContent = agent.is_alive ? "Alive" : `Dead (${agent.cause_of_death || "unknown"})`;

  const learner = agent.learner;
  $("agentLearner").hidden = !learner;
  if (learner) {
    $("learnEpsilon").textContent = num(learner.epsilon, 3);
    $("learnSteps").textContent = dash(learner.steps);
    $("learnQ").textContent = dash(learner.q_entries);
    $("learnState").textContent = learner.last_state ? learner.last_state.join(" · ") : "—";

    const list = $("learnRecent");
    list.replaceChildren();
    for (const item of [...(learner.recent || [])].reverse()) {
      const li = document.createElement("li");
      const a = document.createElement("span");
      a.textContent = ACTION_LABELS[item.action] || item.action;
      const r = document.createElement("span");
      r.textContent = (item.reward > 0 ? "+" : "") + num(item.reward, 2);
      r.className = item.reward > 0 ? "pos" : item.reward < -0.1 ? "neg" : "";
      li.append(a, r);
      list.append(li);
    }
  }
}
