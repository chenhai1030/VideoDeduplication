import { FilterNone } from "@material-ui/icons";

const initialState = {
  headIP: "",
  stopped: true,
  error: false,
  workers: [{
    nodeIP: "",
    status: "off"
  }],
  taskRunning: false,
  startTime: "",
  endTime: "",
};

export default initialState;