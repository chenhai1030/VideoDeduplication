import React, { useCallback, useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import AppPage from "../../../application/components/AppPage";
import { useIntl } from "react-intl";
import { useDispatch, useSelector } from "react-redux";
import { selectRayStatus } from "../../state/selectors"
// import axios from "axios";


const useStyles = makeStyles((theme) => ({
  container: {
    paddingTop: theme.dimensions.content.padding,
    padding: theme.dimensions.content.padding,
    display: "flex",
    flexDirection: "column",
    alignItems: "stretch",
    padding: theme.spacing(2),
    minWidth: 400,
  },
  dashboardiframe:{
    minWidth: 400,
    minHeight:600,
  }
}))

function ProcessingPage(props) {
  const { className } = props;
  const classes = useStyles();
  const intl = useIntl();
  const [count, setCount] = useState(0);
  const rayDashboard = 

  useEffect(() => {
    const timer = setInterval(() => {
      setCount(count + 1);
      // getMessage();
    }, 5000);
    return () => clearInterval(timer);
  }, [count]);

  return (
    <AppPage
    title={intl.formatMessage({ id: "nav.processing" })}
    className={className}
    >
    {/* <div>{count}</div> */}
    <div className={classes.container}>
      <iframe src={intl.formatMessage({ id: "ray.dashboard.addr" })} className={classes.dashboardiframe}></iframe>
    </div>

    </AppPage>);
}


ProcessingPage.propTypes = {
  className: PropTypes.string,
};

export default ProcessingPage;