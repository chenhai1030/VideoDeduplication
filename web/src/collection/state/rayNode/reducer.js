import initialState from "./initialState"; 
import {
  ACTION_RAY_HEAD_LAUNCH,
  ACTION_RAY_WORKER_LAUNCH,
  ACTION_RAY_HEAD_STOP,
  ACTION_RAY_NODE_STOP,
  ACTION_RAY_NODE_STATUS_UPDATE,
  ACTION_RAY_NODE_CLEAN,
  ACTION_RAY_NODE_REMOVE,
  ACTION_RAY_TIMESTAMP_UPDATE,
  ACTION_RAY_TASK_LAUNCH,
  ACTION_RAY_START_HEAD_SUCCESS,
  ACTION_RAY_STOP_NODE_SUCCESS,
  ACTION_RAY_START_WORKER_SUCCESS,
  ACTION_TASK_LAUNCH_SUCCESS,
  ACTION_TASK_STOP_SUCCESS,
} from "./actions";

export default function rayNodeStatusReducer(state = initialState, action) {
  switch (action.type) {
    case ACTION_RAY_HEAD_LAUNCH:
      return {...state,
        ipaddr: action.ipaddr,
      };
    case ACTION_RAY_START_HEAD_SUCCESS:
      state.headIP=action.ipaddr
      state.stopped=false;
      return {...state,};
    case ACTION_RAY_STOP_NODE_SUCCESS:
      if (action.ipaddr == state.headIP){
        state.stopped=true;
      }
      return {...state,};
    case ACTION_RAY_START_WORKER_SUCCESS:
      return {...state,};
    case ACTION_RAY_HEAD_STOP:
      return {...state,
        ipaddr: action.ipaddr,
      };
    case ACTION_RAY_WORKER_LAUNCH:
    case ACTION_RAY_NODE_STOP:
    case ACTION_RAY_NODE_CLEAN:
      return {...state,
        ipaddr: action.ipaddr,
      };
    case ACTION_RAY_NODE_STATUS_UPDATE:
      if (state.workers[0].nodeIP==""){
        state.workers[0].nodeIP = action.nodeIP;
      }else{
        for(let i=0;i< state.workers.length;i++){
          if (action.nodeIP == state.workers[i].nodeIP){
            state.workers[i].status = action.status;
            return {...state,};
          }
        }
        state.workers.push({nodeIP:action.nodeIP, status:action.status});
      }
      return {...state,
        // workers: [  ...state.workers, { nodeIP:action.nodeIP, status:action.status }],
      };
    case ACTION_RAY_NODE_REMOVE:
      for(let i=0; i< state.workers.length; i++){
        if (action.ipaddr == state.workers[i].nodeIP){
          state.workers.splice(i, 1);
          if (state.workers.length == 0){
            state.workers.push({nodeIP:"", status:"off"})
          }
        }
      }
      return {...state,};
    case ACTION_RAY_TIMESTAMP_UPDATE:
      if (action.isStartTime){
        state.startTime = action.timestamp
      }else{
        state.endTime = action.timestamp
      }
      return {...state,};
    case ACTION_RAY_TASK_LAUNCH:
      return {...state,};
    case ACTION_TASK_LAUNCH_SUCCESS:
      state.taskRunning = true;
      return {...state,}
    case ACTION_TASK_STOP_SUCCESS:
      state.taskRunning = false
      return {...state,}
    default:
      return state
  }
}