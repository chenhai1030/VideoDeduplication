import React from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import { useIntl } from "react-intl";
import CleanIcon from "@material-ui/icons/DeleteOutline";
import Hidden from "@material-ui/core/Hidden";
import SquaredIconButton from "../../../common/components/SquaredIconButton";
import Tooltip from "@material-ui/core/Tooltip";
import Button from "../../../common/components/Button";

const useStyles = makeStyles(() => ({
  buttonIcon: {
    marginRight: 12,
  },
}));

function ClearButton(props) {
  const { className, state, onChange} = props
  const classes = useStyles();
  const intl = useIntl();

  const handleClick = (event) => {
    onChange(state);
  }

  return (
    <React.Fragment>
      <Hidden smDown>
        <Button className={className}  onClick={handleClick}>
          <CleanIcon className={classes.buttonIcon} />
          {intl.formatMessage({ id: "actions.CleanNodes" })}
        </Button>
      </Hidden>
      <Hidden mdUp>
        <Tooltip title={intl.formatMessage({ id: "actions.CleanNodes" })}>
          <SquaredIconButton className={className} >
            <CleanIcon />
          </SquaredIconButton>
        </Tooltip>
      </Hidden>
    </React.Fragment>
  );
}

ClearButton.propTypes = {
  className: PropTypes.string,
  onChange: PropTypes.func,
};

export default ClearButton;