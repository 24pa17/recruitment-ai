import ReactMarkdown from "react-markdown";
import { Box } from "@mui/material";

export default function MessageBubble({ message }) {
  return (
    <Box
      sx={{
        mb: 2,
        p: 2,
        borderRadius: 2,
        backgroundColor: message.sender === "user" ? "#1976d2" : "#f1f1f1",
        color: message.sender === "user" ? "#fff" : "#000",
        maxWidth: "70%"
      }}
    >
      {message.type === "text" && (
        <ReactMarkdown>{message.text}</ReactMarkdown>
      )}
    </Box>
  );
}