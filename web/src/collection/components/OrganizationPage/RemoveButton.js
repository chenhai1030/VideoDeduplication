import React from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import { useIntl } from "react-intl";
import RemoveIcon from "@material-ui/icons/RemoveCircleOutline";
import Hidden from "@material-ui/core/Hidden";
import SquaredIconButton from "../../../common/components/SquaredIconButton";
import Tooltip from "@material-ui/core/Tooltip";
import Button from "../../../common/components/Button";

const useStyles = makeStyles(() => ({
  buttonIcon: {
    marginRight: 12,
  },
}));

function RemoveButton(props) {
  const { className, ipaddr, state, onRemove} = props
  const classes = useStyles();
  const intl = useIntl();

  const handleClick = (event) => {
    onRemove(ipaddr);
  }

  return (
    <React.Fragment>
      <Hidden smDown>
        <Button className={className} >
          <RemoveIcon className={classes.buttonIcon} />
          {intl.formatMessage({ id: "actions.RemoveNode" })}
        </Button>
      </Hidden>
      <Hidden mdUp>
        <Tooltip title={intl.formatMessage({ id: "actions.RemoveNode" })}>
          <SquaredIconButton className={className} onClick={handleClick}>
            <RemoveIcon />
          </SquaredIconButton>
        </Tooltip>
      </Hidden>
    </React.Fragment>
  );
}

RemoveButton.propTypes = {
  className: PropTypes.string,
};

export default RemoveButton;