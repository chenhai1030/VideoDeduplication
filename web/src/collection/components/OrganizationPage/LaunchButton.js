import React from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import { useIntl } from "react-intl";
import PlayCircleOutlineIcon from '@material-ui/icons/PlayCircleOutline';
import StopIcon from '@material-ui/icons/Stop';
import Hidden from "@material-ui/core/Hidden";
import SquaredIconButton from "../../../common/components/SquaredIconButton";
import Tooltip from "@material-ui/core/Tooltip";
import Button from "../../../common/components/Button";


const useStyles = makeStyles(() => ({
  buttonIcon: {
    marginRight: 12,
  },
}));

function LaunchButton(props) {
  const { className, state, onLaunch, onStopTask} = props
  const classes = useStyles();
  const intl = useIntl();
  const showStopButton = (state.taskRunning)? true:false;

  const handleClick = () => {
    if (state.stopped){
      console.info("Head(ray) is not started")
    }else{
      onLaunch(state.startTime, state.endTime)
    }
  }

  const handleStopClick = () =>{
    onStopTask()
  }

  return (
    showStopButton?(
    <React.Fragment>
      <Hidden smDown>
        <Button className={className} onClick={handleStopClick}>
          <StopIcon className={classes.buttonIcon} />
          {intl.formatMessage({ id: "actions.stopTask" })}
        </Button>
      </Hidden>
      <Hidden mdUp>
        <Tooltip title={intl.formatMessage({ id: "actions.stopTask" })}>
          <SquaredIconButton className={className} onClick={handleStopClick}>
            <StopIcon />
          </SquaredIconButton>
        </Tooltip>
      </Hidden>
    </React.Fragment>
    ):(
      <React.Fragment>
      <Hidden smDown>
        <Button className={className} onClick={handleClick}>
          <PlayCircleOutlineIcon className={classes.buttonIcon} />
          {intl.formatMessage({ id: "actions.Launch" })}
        </Button>
      </Hidden>
      <Hidden mdUp>
        <Tooltip title={intl.formatMessage({ id: "actions.Launch" })}>
          <SquaredIconButton className={className} onClick={handleClick}>
            <PlayCircleOutlineIcon />
          </SquaredIconButton>
        </Tooltip>
      </Hidden>
      </React.Fragment> 
    )
  );

}

LaunchButton.propTypes = {
  className: PropTypes.string,
};

export default LaunchButton;

