import React, {useCallback} from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import SwitchButton from "./SwitchButton";
import RemoveButton from "./RemoveButton";

const useStyles = makeStyles((theme) => ({
  workernodes:{
    paddingTop: theme.dimensions.content.padding,
    padding: theme.dimensions.content.padding,
  },
  nodeip: {
    fontWeight:700,
  },
  buttons:{
    display: "flex",
  }
}));

function NodeList(props) {
  const { className, onChange, onRemove, state } = props;
  const showList = (props.state.workers[0].nodeIP!=="")? true:false;
  const workers = Array.from(props.state.workers);
  const classes = useStyles();
  // console.info(workers) 
  return (
    showList?(
      <div className={classes.workernodes}> 
        {workers.map((item) => (
          <form key={item.nodeIP}>
            <span className={classes.nodeip}>
              {item.nodeIP}
            </span>
            <div className={classes.buttons}>
              <SwitchButton 
                state={state}
                ipaddr={item.nodeIP}
                status={item.status}
                onChange={onChange}
              />
              <RemoveButton
                state={state}
                ipaddr={item.nodeIP}
                onRemove={onRemove}
              />
            </div>
          </form>
        ))}
      </div>
    ):null
  );
}

NodeList.propTypes = {
  className: PropTypes.string,
};

export default NodeList;