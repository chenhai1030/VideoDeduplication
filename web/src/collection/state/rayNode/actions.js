import { func } from "prop-types";

export const ACTION_RAY_HEAD_LAUNCH = "ray.HEAD_LAUNCH";

export const ACTION_RAY_HEAD_STOP = "ray.HEAD_STOP"

export const ACTION_RAY_WORKER_LAUNCH = "ray.WORKER_LAUNCH";

export const ACTION_RAY_NODE_STOP = "ray.NODE_STOP";

export const ACTION_RAY_NODE_STATUS_UPDATE = "ray.NODE_STATUS_UPDATE";

export const ACTION_RAY_NODE_CLEAN = "ray.NODE_CLEAN";

export const ACTION_RAY_NODE_REMOVE = "ray.NODE_REMOVE";


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
  return { type: ACTION_RAY_NODE_REMOVE, ipaddr};
}

export function updateNodeStatus(nodeIP, status){
  return { type: ACTION_RAY_NODE_STATUS_UPDATE, nodeIP, status};
}