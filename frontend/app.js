
import { connect } from "./services/socket.js";
import * as townMap from "./components/townMap.js";
import * as dashboard from "./components/dashboard.js";
import * as navbar from "./components/navbar.js";
import * as eventButtons from "./components/eventButtons.js";

townMap.init();
dashboard.init();
eventButtons.init();

connect((state) => {
  townMap.setState(state);
  dashboard.update(state);
  navbar.update(state);
  eventButtons.sync(state);
});
