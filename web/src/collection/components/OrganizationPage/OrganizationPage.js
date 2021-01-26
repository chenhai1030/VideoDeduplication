import React, { useCallback, useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import AppPage from "../../../application/components/AppPage";
import { useIntl } from "react-intl";
import HeadNode from "./HeadNode";
import WorkerNode from "./WorkerNode";
import NodeList from "./NodeList";
import { useDispatch, useSelector } from "react-redux";
import { selectRayStatus } from "../../state/selectors";
import {
  launchHead,
  stopHead,
  launchWorkerNode,
  stopNode,
  updateNodeStatus,
} from "../../state/rayNode/actions";


const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.dimensions.content.padding,
    padding: theme.dimensions.content.padding,
    display: "flex",
    alignItems: "stretch",
    minWidth: theme.dimensions.collectionPage.width,
  },
  body: {
    height: "100%",
  },
  dashboard: {
    height: "100%",
  },
  headnode:{
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1)
  },
}))

function OrganizationPage(props) {
  const { className } = props;
  const classes = useStyles();
  const intl = useIntl();
  const dispatch = useDispatch();
  const rayNodeStatus = useSelector(selectRayStatus)
  const headIPaddr =intl.formatMessage({ id: "ray.head.ipaddr" }) 

  const handleAdd = useCallback((nodeIP) => {
    // console.info(nodeIP)
    dispatch(updateNodeStatus(nodeIP, "off"));
  }, []);

  const handleHeadChange = useCallback((ipaddr, status) => {
    if (status == "on"){
      dispatch(launchHead(headIPaddr));
    }else{
      dispatch(stopHead(headIPaddr));
    }
  }, [])

  const handleWorkerChange = useCallback((ipaddr, status) => {
    // console.info(ipaddr)
    // console.info(status);
    // state? dispatch(updateNodeStatus)
    if (status=="on"){
      dispatch(updateNodeStatus(ipaddr, "on"));
      dispatch(launchWorkerNode(ipaddr));
    }else{
      dispatch(updateNodeStatus(ipaddr, "off"));
      dispatch(stopNode(ipaddr));
    }
  }, [])

  return (
    <AppPage
      title={intl.formatMessage({ id: "nav.organization" })}
      className={className}
    >
      <div className={classes.container} role="main">
        <HeadNode
          state={rayNodeStatus}
          onChange={handleHeadChange}
          className={classes.headnode}
          ipaddr={headIPaddr}
        />
      </div>
      <div className={classes.container} >
        <WorkerNode
          // state={rayNodeStatus}
          className={classes.workernode}
          onAdd={handleAdd}
        />
      </div>
      <NodeList
        state={rayNodeStatus}
        onChange={handleWorkerChange}
      /> 
    </AppPage>
  );
}

OrganizationPage.propTypes = {
    className: PropTypes.string,
  };
  
  export default OrganizationPage;
  