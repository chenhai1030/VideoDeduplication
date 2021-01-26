import initialState from "./initialState"; 
import {
  ACTION_RAY_HEAD_LAUNCH,
  ACTION_RAY_WORKER_LAUNCH,
  ACTION_RAY_HEAD_STOP,
  ACTION_RAY_NODE_STOP,
  ACTION_RAY_NODE_STATUS_UPDATE,
} from "./actions";

export default function rayNodeStatusReducer(state = initialState, action) {
  switch (action.type) {
    case ACTION_RAY_HEAD_LAUNCH:
      state.stopped=false;
      return {...state,
        ipaddr: action.ipaddr,
      };
    case ACTION_RAY_HEAD_STOP:
      state.stopped=true;
      return {...state,
        ipaddr: action.ipaddr,
      };
    case ACTION_RAY_WORKER_LAUNCH:
      return {...state,
        ipaddr: action.ipaddr,
      };
    case ACTION_RAY_NODE_STOP:
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
            return {...state};
          }
        }
        state.workers.push({nodeIP:action.nodeIP, status:action.status});
      }
      return {...state,
        // workers: [  ...state.workers, { nodeIP:action.nodeIP, status:action.status }],
      };
    default:
      return state
  }
}