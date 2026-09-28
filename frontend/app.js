import { connect } from "./services/socket.js";
import * as townMap from "C:\Users\Lenovo\OneDrive\Desktop\Simulation-World\Frontend\components/townMap.js";
import * as dashboard from "C:\Users\Lenovo\OneDrive\Desktop\Simulation-World\Frontend\components/dashboard.js";
import * as navbar from "C:\Users\Lenovo\OneDrive\Desktop\Simulation-World\Frontend\components/navbar.js";
import * as eventButtons from "C:\Users\Lenovo\OneDrive\Desktop\Simulation-World\Frontend\components/eventButtons.js";

townMap.init();
dashboard.init();
eventButtons.init();

connect((state) => {
  townMap.setState(state);
  dashboard.update(state);
  navbar.update(state);
  eventButtons.sync(state);
});
