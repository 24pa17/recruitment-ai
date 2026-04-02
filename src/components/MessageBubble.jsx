import { Box, Typography } from "@mui/material";

export default function MessageBubble({ message }) {
  const isUser = message.sender === "user";

  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        mb: 1
      }}
    >
      <Box
        sx={{
          bgcolor: isUser ? "#1976d2" : "#f1f1f1",
          color: isUser ? "white" : "black",
          px: 2,
          py: 1,
          borderRadius: 2,
          maxWidth: "70%"
        }}
      >
        {/* ✅ USER MESSAGE */}
        {isUser ? (
          <Typography>{message.text}</Typography>
        ) : 
        /* ✅ IF MATCHES EXIST → SHOW CARDS */
        message.response?.matches ? (
          message.response.matches.map((item, i) => (
            <Box
              key={i}
              sx={{
                border: "1px solid #ddd",
                borderRadius: 2,
                p: 2,
                mb: 1,
                backgroundColor: i === 0 ? "#d4edda" : "white"
              }}
            >
              <Typography variant="h6">👤 {item.name}</Typography>
              <Typography>🛠 {item.skills}</Typography>
              <Typography>📊 Score: {item.score}%</Typography>
            </Box>
          ))
        ) : (
          /* ✅ NORMAL BOT TEXT */
          <Typography>{message.response?.text}</Typography>
        )}
      </Box>
    </Box>
  );
}