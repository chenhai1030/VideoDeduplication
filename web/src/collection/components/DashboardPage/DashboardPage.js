import React from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import AppPage from "../../../application/components/AppPage";
import { useIntl } from "react-intl";
import Dashboard from "./Dashboard";
import { useSelector } from "react-redux"
import {
  selectFileCounts,
} from "../../state/selectors";

const useStyles = makeStyles(() => ({
  body: {
    height: "100%",
  },
  dashboard: {
    height: "100%",
  },
}));

function DashboardPage(props) {
  const { className } = props;
  const classes = useStyles();
  const intl = useIntl();
  const counts = useSelector(selectFileCounts)

  return (
    <AppPage
      title={intl.formatMessage({ id: "nav.dashboard" })}
      className={className}
    >
      <div className={classes.body} role="main">
        <Dashboard counts={counts}/>
      </div>
    </AppPage>
  );
}

DashboardPage.propTypes = {
  className: PropTypes.string,
};

export default DashboardPage;
