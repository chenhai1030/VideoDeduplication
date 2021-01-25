import React, { useCallback, useEffect, useState } from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import SwitchButton from "./SwitchButton";

const useStyles = makeStyles(() => ({
  headnode: {
    fontWeight:800,
  },
}));

function HeadNode(props){
  const { ipaddr, onChange, className } = props
  const classes = useStyles()

  return (
    <div>
      <h3>HeadNode</h3>
      {/* <TodoList items={this.state.items} /> */}
      <form >
        <span className={classes.headnode}>
          {ipaddr}
        </span>
        <SwitchButton 
          onChange={onChange}
        />
      </form>
    </div>
  );
}

HeadNode.propTypes = {
    className: PropTypes.string,
};
  

export default HeadNode;