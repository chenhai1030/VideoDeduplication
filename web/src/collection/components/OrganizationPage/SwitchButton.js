import React from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import { useIntl } from "react-intl";
import AddIcon from "@material-ui/icons/Add";
import Hidden from "@material-ui/core/Hidden";
import { FormControlLabel , FormGroup, Switch, withStyles} from '@material-ui/core';



const IOSSwitch = withStyles((theme) => ({
  root: {
    width: 42,
    height: 26,
    padding: 0,
    margin: theme.spacing(1),
  },
  switchBase: {
    padding: 1,
    '&$checked': {
      transform: 'translateX(16px)',
      color: theme.palette.common.white,
      '& + $track': {
        backgroundColor: '#52d869',
        opacity: 1,
        border: 'none',
      },
    },
    '&$focusVisible $thumb': {
      color: '#52d869',
      border: '6px solid #fff',
    },
  },
  thumb: {
    width: 24,
    height: 24,
  },
  track: {
    borderRadius: 26 / 2,
    border: `1px solid ${theme.palette.grey[400]}`,
    backgroundColor: theme.palette.grey[50],
    opacity: 1,
    transition: theme.transitions.create(['background-color', 'border']),
  },
  checked: {},
  focusVisible: {},
}))(({ classes, ...props }) => {
  return (
    <Switch
      focusVisibleClassName={classes.focusVisible}
      disableRipple
      classes={{
        root: classes.root,
        switchBase: classes.switchBase,
        thumb: classes.thumb,
        track: classes.track,
        checked: classes.checked,
      }}
      {...props}
    />
  );
});

function SwitchButton(props) {
  const { className, ipaddr, status, onChange} = props;
  const [state, setState] = React.useState({checked: false});
  // console.info(ipaddr);
  // console.info(status);
  const handleChange = (event) => {
    setState({ ...state, [event.target.name]: event.target.checked });
    event.target.checked?onChange(ipaddr, "on"):onChange(ipaddr, "off");
  };

  return (
    <FormGroup>
      <FormControlLabel
        // control={<Switch checked={checked} onChange={toggleChecked} />}
        control = {<IOSSwitch checked={state.checkedA} onChange={handleChange} name="checked"/>}
      />
    </FormGroup>
  );
}

SwitchButton.propTypes = {
  className: PropTypes.string,
};

export default SwitchButton;