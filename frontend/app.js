import { connect } from "./services/socket.js";
import * as townMap from "./components/Townmap.js";
import * as dashboard from "./components/Dashboard.js";
import * as navbar from "./components/Navbar.js";
import * as eventButtons from "./components/Eventbuttons.js";
import * as agentPanel from "./components/AgentPanel.js";

townMap.init();
dashboard.init();
eventButtons.init();
agentPanel.init();
const safe = (name, fn) => (state) => {
  try {
    fn(state);
  } catch (err) {
    console.error(`${name} failed to update:`, err);
  }
};

const handlers = [
  safe("townMap", townMap.setState),
  safe("dashboard", dashboard.update),
  safe("navbar", navbar.update),
  safe("eventButtons", eventButtons.sync),
  safe("agentPanel", agentPanel.update),
];

connect(
  (state) => handlers.forEach((h) => h(state)),
  (status) => navbar.setConnection(status)
);
