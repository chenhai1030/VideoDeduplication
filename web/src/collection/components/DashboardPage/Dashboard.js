import React from "react";
import clsx from "clsx";
import PropTypes from "prop-types";
import { makeStyles } from "@material-ui/styles";
import { useIntl } from "react-intl";
// import DropDownButton from "../../../common/components/DropDownButton";
import PieChart from "./PieChart";
import { useTheme } from "@material-ui/core";
// import BackdropMenu from "./BackdropMenu";
import StackedLineChart from "./StackedLineChart";
import Grid from "@material-ui/core/Grid";
// import useUniqueId from "../../../common/hooks/useUniqueId";
import { formatCount } from "../../../common/helpers/format";
import { MatchCategory } from "../../state/fileList/MatchCategory"

const useStyles = makeStyles((theme) => ({
  dashboardContainer: {
    paddingTop: theme.dimensions.content.padding * 2,
    padding: theme.dimensions.content.padding,
  },
  header: {
    display: "flex",
    alignItems: "center",
  },
  blur: {
    filter: "blur(10px)",
  },
  body: {
    minHeight: "min-content",
    transform: "translate(0%, 0px)",
  },
  content: {
    height: "100%",
    paddingTop: theme.spacing(8),
    padding: theme.spacing(1),
  },
  buttonsPanel: {
    flexGrow: 1,
  },
}));

// function useMessages() {
//   const intl = useIntl();
//   return {
//     dashboard: intl.formatMessage({ id: "collection.dashboard.title" }),
//   };
// }

// This data will be retrieved from server.
const matches = (theme, counts) => [
  {
    name: "Matches",
    value: formatCount(counts["duplicates"]),
    color: theme.palette.primary.main,
  },
  {
    name: "Possibly related",
    value: formatCount(counts["related"]), 
    color: theme.palette.primary.light,
  },
  {
    name: "Unique files",
    value: formatCount(counts["unique"]),
    color: "#131726",
  },
];

// This data will be retrieved from server.
const dbMatches = (theme) => ({
  labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"],
  series: [
    {
      name: "Upcoming",
      data: [25, 27, 21, 21, 22, 30, 20, 21, 40],
      color: theme.palette.primary.light,
    },
    {
      name: "Possibly Related",
      data: [5, 10, 27, 40, 55, 60, 43, 21, 25],
      color: theme.palette.primary.main,
    },
    {
      name: "Completed",
      data: [5, 10, 12, 15, 25, 43, 80, 120, 100],
      color: "#131726",
    },
  ],
});

// function menuActions(intl) {
//   return [
//     {
//       title: intl.formatMessage({ id: "collection.analytics.matches" }),
//       handler: console.log,
//     },
//     {
//       title: intl.formatMessage({ id: "collection.analytics.mediaClass" }),
//       handler: console.log,
//     },
//     {
//       title: intl.formatMessage({ id: "collection.analytics.dbMatches" }),
//       handler: console.log,
//     },
//     {
//       title: intl.formatMessage({ id: "collection.analytics.advancedSearch" }),
//       handler: console.log,
//     },
//     {
//       title: intl.formatMessage({ id: "collection.analytics.collab" }),
//       handler: console.log,
//     },
//   ];
// }

// TODO: Uncomment code when backdrop menu is back again

function Dashboard(props) {
  const { counts, className} = props;
  const classes = useStyles();
  // const messages = useMessages();
  const theme = useTheme();
  const intl = useIntl();
  // const [showMenu, setShowMenu] = useState(false);
  const showMenu = false;
  // const backdropMenuId = useUniqueId("backdrop-menu");
  // console.info(counts)

  return (
    <div className={clsx(classes.dashboardContainer, className)}>
      <div className={classes.header}>
        {/*<DropDownButton*/}
        {/*  title={messages.dashboard}*/}
        {/*  onClick={() => setShowMenu(!showMenu)}*/}
        {/*  aria-haspopup="true"*/}
        {/*  aria-controls={backdropMenuId}*/}
        {/*/>*/}
      </div>
      <div className={classes.body}>
        <div className={clsx(classes.content, { [classes.blur]: showMenu })}>
          <Grid
            container
            spacing={3}
            role="region"
            aria-label={intl.formatMessage({ id: "aria.label.dashboard" })}
          >
            <Grid item lg={6} xs={12}>
              <PieChart title="My Matches" categories={matches(theme, counts)}/>
            </Grid>
            {/* <Grid item lg={6} xs={12}>
              <StackedLineChart
                title="Database Matches"
                {...dbMatches(theme)}
              />
            </Grid> */}
          </Grid>
        </div>
        {/*<BackdropMenu*/}
        {/*  id={backdropMenuId}*/}
        {/*  actions={menuActions(intl)}*/}
        {/*  open={showMenu}*/}
        {/*  onClose={() => setShowMenu(false)}*/}
        {/*/>*/}
      </div>
    </div>
  );
}

Dashboard.propTypes = {
  counts: PropTypes.shape({
    [MatchCategory.all]: PropTypes.number.isRequired,
    [MatchCategory.duplicates]: PropTypes.number.isRequired,
    [MatchCategory.related]: PropTypes.number.isRequired,
    [MatchCategory.unique]: PropTypes.number.isRequired,
  }).isRequired,
  className: PropTypes.string,
};

export default Dashboard;
