import React from "react";
import { Card, CardContent, Typography } from "@mui/material";

export default function CardResponse({ data }) {
  return (
    <Card sx={{ mt: 2 }}>
      <CardContent>
        <Typography variant="h6">{data.title}</Typography>
        <Typography variant="subtitle1">{data.subtitle}</Typography>

        {data.fields?.map((field, i) => (
          <Typography key={i}>
            <b>{field.label}:</b> {field.value}
          </Typography>
        ))}
      </CardContent>
    </Card>
  );
}
