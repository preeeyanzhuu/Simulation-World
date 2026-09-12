

export function update(state) {
  document.getElementById("clockDay").textContent = `Day ${state.day}`;
  document.getElementById("clockTime").textContent =
    `${String(state.hour).padStart(2, "0")}:00`;
  document.getElementById("clockWeather").textContent = state.weather;
}
