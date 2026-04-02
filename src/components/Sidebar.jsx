import { Box, Button, Typography } from "@mui/material";

export default function Sidebar() {
  return (
    <Box sx={{
      width: "250px",
      background: "white",
      padding: 2,
      borderRight: "1px solid #ddd"
    }}>
      <Typography variant="h6" sx={{ mb: 2 }}>
        Recruitment AI
      </Typography>

      <Button fullWidth variant="contained" sx={{ mb: 2 }}>
        + New Chat
      </Button>

      <Typography variant="body2" color="gray">Conversations</Typography>
    </Box>
  );
}
