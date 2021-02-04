import React, { useCallback } from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import { TextField } from '@material-ui/core';

const useStyles = makeStyles(() => ({
  container:{
    display: "flex",
  },
  dateIcon: {
    marginRight: 12,
  },
  textField: {
    display: "flex",
  },
}));


function DatePane(props) {
  const { className, onFromDateChange, onToDateChange} = props;
  const classes = useStyles();

  const handleFromChange = useCallback((event) => onFromDateChange(event.target.value), [
  ]);

  const handleToChange = useCallback((event) => onToDateChange(event.target.value), [
  ]);

  return (
    <div>
      <form className={classes.container} noValidate>
        <TextField
          id="datetime-local"
          label="From"
          type="datetime-local"
          defaultValue="2021-02-03T10:00"
          className={classes.textField}
          onChange={handleFromChange}
          InputLabelProps={{
            shrink: true,
          }}
        />
      </form>
      <form className={classes.container} noValidate>
        <TextField
          id="datetime-local"
          label="To"
          type="datetime-local"
          defaultValue="2021-02-03T20:00"
          className={classes.textField}
          onChange={handleToChange}
          InputLabelProps={{
            shrink: true,
          }}
        />
      </form>
    </div>
  );
}

DatePane.propTypes = {
  className: PropTypes.string,
};

export default DatePane;