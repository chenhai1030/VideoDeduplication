import { call, put, takeLatest } from "redux-saga/effects";
import {
  ACTION_RAY_HEAD_LAUNCH,
  ACTION_RAY_HEAD_STOP,
  ACTION_RAY_WORKER_LAUNCH,
  ACTION_RAY_NODE_STOP,
  ACTION_RAY_NODE_CLEAN,
  ACTION_RAY_NODE_REMOVE,
  ACTION_RAY_NODE_STATUS_UPDATE,
  ACTION_RAY_TIMESTAMP_UPDATE,
  ACTION_RAY_TASK_LAUNCH,
  ACTION_RAY_TASK_STOP,
  rayStartHeadSuccess,
  rayStartHeadFailure,
  rayStopNodeSuccess,
  rayStopNodeFailure,
  rayStartWorkerSuccess,
  rayStartWorkerFailure,
  launchTaskSuccess,
  launchTaskFailure,
  stopTaskSuccess,
  stopTaskFailure,
  cleanNodeSuccess,
  cleanNodeFailure,
} from "./actions"

function resolvRayActions(rayAction) {
  switch (rayAction.type) {
    case ACTION_RAY_HEAD_LAUNCH:
      return [rayStartHeadSuccess, rayStartHeadFailure];
    case ACTION_RAY_HEAD_STOP:
    case ACTION_RAY_NODE_STOP:
      return [rayStopNodeSuccess, rayStopNodeFailure];
    case ACTION_RAY_WORKER_LAUNCH:
      return [rayStartWorkerSuccess, rayStartWorkerFailure];
    case ACTION_RAY_TASK_LAUNCH:
      return [launchTaskSuccess, launchTaskFailure];
    case ACTION_RAY_TASK_STOP:
      return [stopTaskSuccess, stopTaskFailure];
    case ACTION_RAY_NODE_CLEAN:
      return [cleanNodeSuccess, cleanNodeFailure];
    // default:
    //   throw new Error(`Unsupported ray action type: ${rayAction.type}`);
  }
}

function* fetchRayNodeSaga(server, selectRayNodeState, action){
  // Determine report-result actions
  const [success, failure] = resolvRayActions(action);

  switch(action.type){
    case ACTION_RAY_HEAD_LAUNCH:
      try{
        const resp = yield call([server, server.rayHeadNodeLaunch], action.ipaddr)
        // Handle error
        if (resp.failure) {
          console.error("start head error", resp.error);
          yield put(failure(resp.error));
          return;
        } 
        // Update state
        yield put(success(action.ipaddr));
      }catch (e){
        console.log(e)
      }   
      return "";
    case ACTION_RAY_WORKER_LAUNCH:
        try{
          const resp = yield call([server, server.rayWorkerNodeLaunch], action.ipaddr)
          // Handle error
          if (resp.failure) {
            console.error("stop node error", resp.error);
            yield put(failure(resp.error));
            return;
          } 
          // Update state
          yield put(success(action.ipaddr));
        }catch (e){
          console.log(e)
        }   
        return "";
    case ACTION_RAY_NODE_STOP:
    case ACTION_RAY_HEAD_STOP:
      try{
        const resp = yield call([server, server.rayNodeStop], action.ipaddr)
        // Handle error
        if (resp.failure) {
          console.error("stop node error", resp.error);
          yield put(failure(resp.error));
          return;
        }
        // Update state
        yield put(success(action.ipaddr));
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
    case ACTION_RAY_TIMESTAMP_UPDATE:
      // const ret = yield call([server, server.rayNodeClean], action)
      return "";
    case ACTION_RAY_TASK_LAUNCH:
      try{
        const resp = yield call([server, server.rayTaskLaunch], action.startTime, action.endTime)
        console.info(resp)
        if (resp.failure) {
          console.error("start task error", resp.error);
          yield put(failure(resp.error));
          return;
        }
        // Update state
        yield put(success());
      }catch (e){
        console.log(e)
      }
      return "";
    case ACTION_RAY_TASK_STOP:
      try{
        const resp = yield call([server, server.rayTaskStop])
        if (resp.failure) {
          console.error("start task error", resp.error);
          yield put(failure(resp.error));
          return;
        }
        // Update state
        yield put(success());
      }catch (e){
        console.log(e)
      }
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
      ACTION_RAY_NODE_STOP, ACTION_RAY_NODE_CLEAN, ACTION_RAY_NODE_REMOVE, ACTION_RAY_TASK_LAUNCH, ACTION_RAY_TASK_STOP],
    fetchRayNodeSaga,
    server,
    selectRayNodeState
  );
}
