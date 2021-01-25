export const ACTION_RAY_HEAD_LAUNCH = "ray.HEAD_LAUNCH";

export const ACTION_RAY_WORKER_LAUNCH = "ray.WORKER_LAUNCH";

export const ACTION_RAY_NODE_STOP = "ray.HEAD_STOP";

export const ACTION_RAY_NODE_STATUS_UPDATE = "ray.RAY_NODE_STATUS_UPDATE";


export function launchHead(ipaddr) {
  return { type: ACTION_RAY_HEAD_LAUNCH, ipaddr };
}

export function launchWorkerNode(ipaddr) {
  return { type: ACTION_RAY_WORKER_LAUNCH, ipaddr };
}

export function stopNode(ipaddr) {
  return { type: ACTION_RAY_NODE_STOP, ipaddr };
}

export function updateNodeStatus(nodeIP, status){
  return { type: ACTION_RAY_NODE_STATUS_UPDATE, nodeIP, status};
}