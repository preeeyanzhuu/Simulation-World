

import { send } from "../services/socket.js";

export function init() {
  document.getElementById("rainBtn").addEventListener("click", () => {
    send("rain");
  });
  document.getElementById("roadClosureBtn").addEventListener("click", () => {
    send("road_closure");
  });
  document.getElementById("taxBtn").addEventListener("click", () => {
    send("tax_hike");
  });
}

export function sync(state) {
  document.getElementById("rainBtn").classList.toggle("is-active", state.weather === "Rain");
  document.getElementById("roadClosureBtn").classList.toggle("is-active", state.roadClosureActive);
  document.getElementById("taxBtn").classList.toggle("is-active", state.taxActive);
}
