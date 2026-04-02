import React, { useState } from "react";
import { askAI } from "../services/api";
import { Box, TextField, IconButton, Typography } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";
import MessageBubble from "./MessageBubble";
import Sidebar from "./Sidebar";
import SuggestionButtons from "./SuggestionButtons";

export default function ChatBot() {
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      response: {
        text: "Hello! I'm your Recruitment Assistant AI. I can help with job openings, candidate matching, interviews and policies."
      }
    }
  ]);

  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    // USER MESSAGE
    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);

    try {
      // ✅ CALL BACKEND (NOT OLLAMA DIRECTLY)
      const aiReply = await askAI(input);

      const botMsg = {
        sender: "bot",
        response: { text: aiReply }
      };

      setMessages((prev) => [...prev, botMsg]);

    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          response: { text: "Server error. Please try again." }
        }
      ]);
    }

    setInput("");
  };

  return (
    <Box sx={{ display: "flex", width: "100%", height: "100vh" }}>
      <Sidebar />

      <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <Box sx={{ p: 2, borderBottom: "1px solid #ddd" }}>
          <Typography variant="h5">Recruitment Assistant</Typography>
        </Box>

        <Box sx={{ flex: 1, overflowY: "auto", p: 2 }}>
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}

          <SuggestionButtons onClick={setInput} />
        </Box>

        <Box sx={{ display: "flex", p: 2, borderTop: "1px solid #ddd" }}>
          <TextField
            fullWidth
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about jobs, candidates, interviews..."
            onKeyPress={(e) => e.key === "Enter" && handleSend()}
          />
          <IconButton color="primary" onClick={handleSend}>
            <SendIcon />
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
}