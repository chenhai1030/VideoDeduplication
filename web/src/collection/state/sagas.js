import { fork } from "redux-saga/effects";
import {
  selectFileCluster,
  selectFileList,
  selectFileMatches,
  selectRayStatus,
} from "./selectors";
import fileMatchRootSaga from "./fileMatches/sagas";
import fileClusterRootSaga from "./fileCluster/sagas";
import fileListRootSaga from "./fileList/sagas";

import rayNodeRootSaga from "./rayNode/sagas";

/**
 * Initialize collection-related sagas...
 */
export default function* collRootSaga(server) {
  yield fork(fileListRootSaga, server, selectFileList);
  yield fork(fileMatchRootSaga, server, selectFileMatches);
  yield fork(fileClusterRootSaga, server, selectFileCluster);
  yield fork(rayNodeRootSaga, server, selectRayStatus);
}
