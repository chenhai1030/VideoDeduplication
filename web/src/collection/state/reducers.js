import fileCacheReducer from "./fileCache/reducer";
import fileMatchesReducer from "./fileMatches/reducer";
import fileClusterReducer from "./fileCluster/reducer";
import { combineReducers } from "redux";
import fileListReducer from "./fileList/reducer";

import rayNodeStatusReducer from "./rayNode/reducer";

const collRootReducer = combineReducers({
  fileList: fileListReducer,
  fileCache: fileCacheReducer,
  fileCluster: fileClusterReducer,
  fileMatches: fileMatchesReducer,
  rayStatus: rayNodeStatusReducer,
});

export default collRootReducer;
