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
      type: "text",
      text: "Hello! I'm your Recruitment Assistant AI. I can help with job openings, candidate matching, interviews and policies."
    }
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = {
      sender: "user",
      type: "text",
      text: input
    };

    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await askAI(input);
      console.log("API RESPONSE:", res); // 🔥 DEBUG

      let newMessages = [];

      // ✅ TEXT RESPONSE
      if (res?.reply) {
        newMessages.push({
          sender: "bot",
          type: "text",
          text: res.reply
        });
      }

      // ✅ CANDIDATE MATCHES
      if (res?.matches && res.matches.length > 0) {
        newMessages.push({
          sender: "bot",
          type: "candidates",
          data: res.matches
        });
      }

      // ❌ FALLBACK
      if (newMessages.length === 0) {
        newMessages.push({
          sender: "bot",
          type: "text",
          text: "No response from AI"
        });
      }

      setMessages((prev) => [...prev, ...newMessages]);

    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          type: "text",
          text: "⚠️ Server error. Please try again."
        }
      ]);
    }

    setLoading(false);
    setInput("");
  };

  return (
    <Box sx={{ display: "flex", width: "100%", height: "100vh" }}>
      
      {/* Sidebar */}
      <Sidebar />

      {/* Main Chat Area */}
      <Box sx={{ flex: 1, display: "flex", flexDirection: "column" }}>
        
        {/* Header */}
        <Box sx={{ p: 2, borderBottom: "1px solid #ddd" }}>
          <Typography variant="h5">Recruitment Assistant</Typography>
        </Box>

        {/* Messages */}
        <Box sx={{ flex: 1, overflowY: "auto", p: 2 }}>
          {messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))}

          {loading && (
            <Typography sx={{ mt: 1, color: "gray" }}>
              AI is typing...
            </Typography>
          )}

          <SuggestionButtons onClick={setInput} />
        </Box>

        {/* Input */}
        <Box sx={{ display: "flex", p: 2, borderTop: "1px solid #ddd" }}>
          <TextField
            fullWidth
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about jobs, candidates..."
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                handleSend();
              }
            }}
          />

          <IconButton color="primary" onClick={handleSend}>
            <SendIcon />
          </IconButton>
        </Box>

      </Box>
    </Box>
  );
}