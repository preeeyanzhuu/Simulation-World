import { send } from "../services/socket.js";

const $ = (id) => document.getElementById(id);

export function init() {
  $("rainBtn").addEventListener("click", () => send("rain"));
  $("taxBtn").addEventListener("click", () => send("tax_hike"));
  $("roadClosureBtn").addEventListener("click", () => {
    send("road_closure", { roadId: $("roadSelect").value });
  });

  let running = true;
  $("simToggleBtn").addEventListener("click", () => send(running ? "sim_stop" : "sim_start"));
  $("simResetBtn").addEventListener("click", () => send("sim_reset"));
  init.setRunning = (value) => { running = value; };
}

function populateRoads(roads) {
  const select = $("roadSelect");
  if (select.options.length || !roads.length) return;
  for (const r of roads) {
    const opt = document.createElement("option");
    opt.value = r.id;
    opt.textContent = r.id.replaceAll("_", " ");
    select.append(opt);
  }
  select.value = roads.some((r) => r.id === "middle_road") ? "middle_road" : roads[0].id;
}

export function sync(state) {
  populateRoads(state.roads);

  $("rainBtn").classList.toggle("is-active", state.weather === "Rain");
  $("roadClosureBtn").classList.toggle("is-active", state.roadClosureActive);
  $("taxBtn").classList.toggle("is-active", state.taxActive);

  if (init.setRunning) init.setRunning(state.running);
  $("simToggleBtn").querySelector(".event-btn-label").textContent = state.running ? "Pause" : "Resume";
  $("simToggleBtn").classList.toggle("is-active", !state.running);
}
