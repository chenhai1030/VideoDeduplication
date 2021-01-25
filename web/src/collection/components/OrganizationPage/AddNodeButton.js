import React from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import { useIntl } from "react-intl";
import AddIcon from "@material-ui/icons/Add";
import Hidden from "@material-ui/core/Hidden";
import SquaredIconButton from "../../../common/components/SquaredIconButton";
import Tooltip from "@material-ui/core/Tooltip";
import Button from "../../../common/components/Button";

const useStyles = makeStyles(() => ({
  buttonIcon: {
    marginRight: 12,
  },
}));

function AddNodeButton(props) {
  const { className, ...other } = props;
  const classes = useStyles();
  const intl = useIntl();
  return (
    <React.Fragment>
      <Hidden smDown>
        <Button className={className} {...other}>
          <AddIcon className={classes.buttonIcon} />
          {intl.formatMessage({ id: "actions.addNode" })}
        </Button>
      </Hidden>
      <Hidden mdUp>
        <Tooltip title={intl.formatMessage({ id: "actions.addNode" })}>
          <SquaredIconButton className={className} {...other}>
            <AddIcon />
          </SquaredIconButton>
        </Tooltip>
      </Hidden>
    </React.Fragment>
  );
}

AddNodeButton.propTypes = {
  className: PropTypes.string,
};

export default AddNodeButton;
