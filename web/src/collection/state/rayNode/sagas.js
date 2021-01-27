import { call, put, select, takeLatest } from "redux-saga/effects";
import {
  ACTION_RAY_HEAD_LAUNCH,
  ACTION_RAY_HEAD_STOP,
  ACTION_RAY_WORKER_LAUNCH,
  ACTION_RAY_NODE_STOP,
  ACTION_RAY_NODE_CLEAN,
  ACTION_RAY_NODE_REMOVE,
  ACTION_RAY_NODE_STATUS_UPDATE,
} from "./actions"

function* fetchRayNodeSaga(server, selectRayNodeState, action){
  switch(action.type){
    case ACTION_RAY_HEAD_LAUNCH:
      try{
        const ret = yield call([server, server.rayHeadNodeLaunch], action.ipaddr)
        // console.log(ret)
      }catch (e){
        console.log(e)
      }   
      return "";
    case ACTION_RAY_WORKER_LAUNCH:
        try{
          const ret = yield call([server, server.rayWorkerNodeLaunch], action.ipaddr)
          // console.log(ret)
        }catch (e){
          console.log(e)
        }   
        return "";
    case ACTION_RAY_NODE_STOP:
    case ACTION_RAY_HEAD_STOP:
      try{
        const ret = yield call([server, server.rayNodeStop], action.ipaddr)
        // console.log(ret)
      }catch (e){
        console.log(e)
      }
      return "";
    case ACTION_RAY_NODE_CLEAN:
      try{
        const ret = yield call([server, server.rayNodeClean], action.ipaddr)
        // console.log(ret)
      }catch (e){
        console.log(e)
      }
      return "";
    case ACTION_RAY_NODE_STATUS_UPDATE:
      try {
        console.info(selectRayNodeState)
      }catch (e){
        console.log(e)
      }
      return "";
    case ACTION_RAY_NODE_REMOVE:
      // console.info(selectRayNodeState);
      return "";
    default:
      return "";
   }
}

/**
 * Initialize rayNode-related sagas...
 */
export default function* rayNodeRootSaga(server, selectRayNodeState) {
  yield takeLatest(
    [ACTION_RAY_HEAD_LAUNCH, ACTION_RAY_HEAD_STOP, ACTION_RAY_WORKER_LAUNCH, 
      ACTION_RAY_NODE_STOP, ACTION_RAY_NODE_CLEAN, ACTION_RAY_NODE_REMOVE],
    fetchRayNodeSaga,
    server,
    selectRayNodeState
  );
}
