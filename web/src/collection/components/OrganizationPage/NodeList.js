import React, {useCallback} from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import SwitchButton from "./SwitchButton";

function NodeList(props) {
  const { className, onChange, state } = props;
  const showList = (props.state.workers[0].nodeIP!=="")? true:false;
  const workers = Array.from(props.state.workers);

  // console.info(workers) 
  return (
    showList?(
      <ul>
        {workers.map((item) => (
        <div key={item.nodeIP}>
          <li>{item.nodeIP}</li>
          <SwitchButton 
            state={state}
            ipaddr={item.nodeIP}
            status={item.status}
            onChange={onChange}
          />
        </div>
        ))}
      </ul>
    ):null
  );
}

NodeList.propTypes = {
  className: PropTypes.string,
};

export default NodeList;