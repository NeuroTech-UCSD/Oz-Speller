import React, { Fragment } from "react";

import { Divider, List, ListItem, ListItemText } from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles({
  list: {
    maxHeight: 546,
    overflow: "auto"
  }
});

function EventList({ events }) {
  const classes = useStyles();

  return (
    <List className={classes.list} dense>
      {events.length > 0 && <Divider />}
      {events.map((item, index) => (
        <Fragment key={index}>
          <ListItem>
            <ListItemText primary={item[0]} secondary={item[1]} />
          </ListItem>
          <Divider />
        </Fragment>
      ))}
    </List>
  );
}

export default EventList;
