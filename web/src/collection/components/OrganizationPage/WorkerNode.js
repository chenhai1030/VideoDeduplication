import React, { useCallback, useEffect, useState } from "react";
import clsx from "clsx"
import { makeStyles } from "@material-ui/styles";
import FormControl from "@material-ui/core/FormControl"
import InputLabel from "@material-ui/core/InputLabel"
import OutlinedInput from "@material-ui/core/OutlinedInput";
import useUniqueId from "../../../common/hooks/useUniqueId";
import { useIntl } from "react-intl";
import PropTypes from "prop-types";
import AddNodeButton from "./AddNodeButton";


const useStyles = makeStyles(() => ({
  input: {
    backgroundColor: "#EBEBEB",
  },
}));
  
function useMessages() {
  const intl = useIntl();
  return {
    node: intl.formatMessage({ id: "actions.nodeFingerprints" }),
  };
}

function WorkerNode(props){
  const { query: queryAttr = "", onAdd, className } = props
  const classes = useStyles()
  const nodeId = useUniqueId("node-input");
  const messages = useMessages()
  const [query, setQuery] = useState(queryAttr)
  const [timeoutHandle, setTimeoutHandle] = useState(null)

  const handleChange = useCallback((event) => setQuery(event.target.value), []);
  const handleClear = useCallback(() => setQuery(""), []);

  const handleAdd = useCallback(() => {
    clearTimeout(timeoutHandle);
    if (query !== queryAttr) {
      onAdd(query);
    }
  }, [query, onAdd, timeoutHandle]);

  const handleControlKeys = useCallback(
    (event) => {
      if (event.key === "Enter") {
        handleAdd();
      } else if (event.key === "Escape") {
        handleClear();
      }
    },
    [handleAdd]
  );

  const handleAddNode = useCallback(() => {
      // console.log(query)
      onAdd(query)
    }
  );

  // useEffect(() => {
  //   clearTimeout(timeoutHandle);
  //   const newHandle = setTimeout(handleAdd, 1000);
  //   setTimeoutHandle(newHandle);
  //   return () => clearTimeout(newHandle);
  // }, [query, onAdd]);

  useEffect(() => {
    if (query !== queryAttr) {
      setQuery(queryAttr);
    }
  }, [queryAttr])

  return (
    <div>
        <h3>WorkerNode</h3>
        <FormControl 
            className={clsx(classes.input, className)}
            variant="outlined"
            size="small"
            color="secondary"
          >
            <InputLabel htmlFor={nodeId}>{messages.node}</InputLabel>
            <OutlinedInput
              id={nodeId}
              type="text"
              value={query}
              onChange={handleChange}
              labelWidth={60}
              onKeyDown={handleControlKeys}
            />
        </FormControl>
        <AddNodeButton
          onClick={handleAddNode}
          variant="contained"
          color="primary"
          className={classes.action}
        />
    </div>
  );
}


WorkerNode.propTypes = {
    query: PropTypes.string,
    onAdd: PropTypes.func,
    className: PropTypes.string,
};
  
export default WorkerNode;