import React from "react";
import { List, ListItem } from "@mui/material";

export default function ListResponse({ data }) {
  return (
    <div>
      <p>{data.text}</p>
      <List>
        {data.items.map((item, i) => (
          <ListItem key={i}>• {item}</ListItem>
        ))}
      </List>
      <small>{data.note}</small>
    </div>
  );
}
