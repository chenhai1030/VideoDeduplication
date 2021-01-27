import React, { useCallback, useEffect, useState } from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import SwitchButton from "./SwitchButton";
import ClearButton from "./ClearButton";

const useStyles = makeStyles(() => ({
  headnode: {
    fontWeight:800,
  },
  buttons:{
    display: "flex",
  }
}));

function HeadNode(props){
  const { ipaddr, state, onChange, onClear, className } = props;
  const classes = useStyles();

  return (
    <div>
      <h3>HeadNode</h3>
      <form >
        <span className={classes.headnode}>
          {ipaddr}
        </span>
        <div className={classes.buttons}>
          <SwitchButton 
            isStopped={state.stopped}
            onChange={onChange}
          />
          <ClearButton
            onChange={onClear}
            state={state}
            variant="contained"
            color="primary"
            className={classes.action}
          />
        </div>
      </form>
    </div>
  );
}

HeadNode.propTypes = {
    className: PropTypes.string,
    onClear: PropTypes.func,
};
  

export default HeadNode;