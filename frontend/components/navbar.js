export function update(state) {
  document.getElementById("clockDay").textContent = `Day ${state.day}`;
  document.getElementById("clockTime").textContent =
    `${String(state.hour).padStart(2, "0")}:00`;
  document.getElementById("clockWeather").textContent = state.weather;

  const { population, totalCitizens } = state.stats;
  document.getElementById("agentCount").textContent =
    population === totalCitizens
      ? `${population} citizens`
      : `${population} alive / ${totalCitizens} citizens`;
}

export function setConnection(status) {
  const el = document.getElementById("connStatus");
  if (!el) return;
  el.textContent = status === "connected" ? "Live" : "Reconnecting…";
  el.classList.toggle("is-offline", status !== "connected");
}
