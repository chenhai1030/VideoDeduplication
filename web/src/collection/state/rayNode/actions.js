import { func } from "prop-types";

export const ACTION_RAY_HEAD_LAUNCH = "ray.HEAD_LAUNCH";
export const ACTION_RAY_HEAD_STOP = "ray.HEAD_STOP"
export const ACTION_RAY_WORKER_LAUNCH = "ray.WORKER_LAUNCH";
export const ACTION_RAY_NODE_STOP = "ray.NODE_STOP";
export const ACTION_RAY_NODE_STATUS_UPDATE = "ray.NODE_STATUS_UPDATE";
export const ACTION_RAY_NODE_CLEAN = "ray.NODE_CLEAN";
export const ACTION_RAY_NODE_REMOVE = "ray.NODE_REMOVE";
export const ACTION_RAY_TIMESTAMP_UPDATE = "ray.TIMESTAMP_UPDATE";
export const ACTION_RAY_TASK_LAUNCH = "ray.TASK_LAUNCH";
export const ACTION_RAY_TASK_STOP = "ray.TASK_STOP";

export const ACTION_RAY_START_HEAD_SUCCESS = "ray.START_HEAD_SUCCESS";
export const ACTION_RAY_START_HEAD_FAILURE = "ray.START_HEAD_FAILURE";
export const ACTION_RAY_STOP_NODE_SUCCESS = "ray.STOP_NODE_SUCCESS";
export const ACTION_RAY_STOP_NODE_FAILURE = "ray.STOP_NODE_FAILURE";
export const ACTION_RAY_START_WORKER_SUCCESS = "ray.START_WORKER_SUCCESS";
export const ACTION_RAY_START_WORKER_FAILURE = "ray.START_WORKER_FAILURE";
export const ACTION_TASK_LAUNCH_SUCCESS = "ray.TASK_LAUNCH_SUCCESS";
export const ACTION_TASK_LAUNCH_FAILURE = "ray.TASK_LAUNCH_FAILURE ";
export const ACTION_TASK_STOP_SUCCESS = "ray.TASK_STOP_SUCCESS";
export const ACTION_TASK_STOP_FAILURE = "ray.TASK_STOP_FAILURE ";
export const ACTION_RAY_NODE_CLEAN_SUCCESS = "ray.NODE_CLEAN_SUCCESS";
export const ACTION_RAY_NODE_CLEAN_FAILURE = "ray.NODE_CLEAN_FAILURE";

export function rayStartHeadSuccess(ipaddr) {
  return { type: ACTION_RAY_START_HEAD_SUCCESS, ipaddr};
}

export function rayStartHeadFailure(error) {
  return { type: ACTION_RAY_START_HEAD_FAILURE, error};
}

export function rayStartWorkerSuccess() {
  return { type: ACTION_RAY_START_WORKER_SUCCESS};
}

export function rayStartWorkerFailure(error) {
  return { type: ACTION_RAY_START_WORKER_FAILURE, error};
}

export function rayStopNode(ipaddr) {
  return { type: ACTION_RAY_STOP_NODE, ipaddr};
}

export function rayStopNodeSuccess(ipaddr){
  return { type: ACTION_RAY_STOP_NODE_SUCCESS, ipaddr};
}

export function rayStopNodeFailure(error){
  return { type: ACTION_RAY_STOP_NODE_FAILURE, error};
}

export function launchTaskSuccess() {
  return { type: ACTION_TASK_LAUNCH_SUCCESS };
}

export function launchTaskFailure(error) {
  return { type: ACTION_TASK_LAUNCH_FAILURE, error };
}

export function launchHead(ipaddr) {
  return { type: ACTION_RAY_HEAD_LAUNCH, ipaddr };
}

export function launchWorkerNode(ipaddr) {
  return { type: ACTION_RAY_WORKER_LAUNCH, ipaddr };
}

export function stopHead(ipaddr) {
  return { type: ACTION_RAY_HEAD_STOP, ipaddr };
}

export function stopNode(ipaddr) {
  return { type: ACTION_RAY_NODE_STOP, ipaddr };
}

export function cleanNode(ipaddr) {
  return { type: ACTION_RAY_NODE_CLEAN, ipaddr };
}

export function removeNode(ipaddr) {
  return { type: ACTION_RAY_NODE_REMOVE, ipaddr };
}

export function updateNodeStatus(nodeIP, status){
  return { type: ACTION_RAY_NODE_STATUS_UPDATE, nodeIP, status };
}

export function updateTimeStamp(isStartTime, timestamp){
  return { type: ACTION_RAY_TIMESTAMP_UPDATE, isStartTime, timestamp };
}

export function launchTask(startTime, endTime) {
  return { type: ACTION_RAY_TASK_LAUNCH, startTime, endTime };
}

export function stopTask(){
  return { type: ACTION_RAY_TASK_STOP}
}

export function stopTaskSuccess() {
  return { type: ACTION_TASK_STOP_SUCCESS };
}

export function stopTaskFailure(error) {
  return { type: ACTION_TASK_STOP_FAILURE, error };
}

export function cleanNodeSuccess(){
  return { type: ACTION_RAY_NODE_CLEAN_SUCCESS};
}

export function cleanNodeFailure(){
  return { type: ACTION_RAY_NODE_CLEAN_FAILURE}
}