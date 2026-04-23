import React from "react";
import { Box, Typography, Chip } from "@mui/material";

export default function MessageBubble({ message }) {
  const isUser = message.sender === "user";

  const bubbleStyle = {
    maxWidth: "70%",
    p: 2,
    borderRadius: 3,
    mb: 2,
    alignSelf: isUser ? "flex-end" : "flex-start",
    backgroundColor: isUser ? "#1976d2" : "#f1f1f1",
    color: isUser ? "white" : "black"
  };

  if (message.type === "text") {
    return (
      <Box sx={{ display: "flex", flexDirection: "column" }}>
        <Box sx={bubbleStyle}>
          <Typography>{message.text}</Typography>
        </Box>
      </Box>
    );
  }

  if (message.type === "job_result") {
    const { job_title, required_skills = [], candidates = [] } = message.data || {};

    return (
      <Box sx={{ display: "flex", flexDirection: "column" }}>
        <Box sx={bubbleStyle}>
          <Typography variant="h6">
            💼 Job Title: {job_title || "N/A"}
          </Typography>

          <Typography sx={{ mt: 1, fontWeight: "bold" }}>
            Required Skills:
          </Typography>

          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mt: 1 }}>
            {required_skills.length > 0 ? (
              required_skills.map((skill, i) => (
                <Chip key={i} label={skill} size="small" />
              ))
            ) : (
              <Typography>No skills provided</Typography>
            )}
          </Box>

          <Typography sx={{ mt: 2, fontWeight: "bold" }}>
            Matched Candidates:
          </Typography>

          {candidates.length === 0 ? (
            <Typography>No candidates found</Typography>
          ) : (
            candidates.map((c, i) => (
              <Box
                key={i}
                sx={{
                  border: "1px solid #ccc",
                  borderRadius: 2,
                  p: 1,
                  mt: 1,
                  backgroundColor: "#fff",
                  color: "#000"
                }}
              >
                <Typography><b>{c.name}</b></Typography>

                <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1, mt: 1 }}>
                  {(c.skills || []).map((skill, idx) => (
                    <Chip key={idx} label={skill} size="small" />
                  ))}
                </Box>

                <Typography sx={{ color: "green", mt: 1 }}>
                  Score: {c.score}
                </Typography>
              </Box>
            ))
          )}
        </Box>
      </Box>
    );
  }

  if (message.type === "job_list") {
    const jobs = message.jobs || [];

    return (
      <Box sx={{ display: "flex", flexDirection: "column" }}>
        <Box sx={bubbleStyle}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            📢 Job Openings
          </Typography>

          {jobs.length === 0 ? (
            <Typography>No job openings found</Typography>
          ) : (
            jobs.map((job, i) => (
              <Box
                key={i}
                sx={{
                  border: "1px solid #ccc",
                  borderRadius: 2,
                  p: 2,
                  mt: 1.5,
                  backgroundColor: "#fff",
                  color: "#000"
                }}
              >
                <Typography sx={{ fontWeight: "bold", mb: 1 }}>
                  Job Role: {job.title}
                </Typography>

                <Typography sx={{ mb: 1 }}>
                  <b>Description (Needed Skills):</b> {job.description}
                </Typography>

                <Typography sx={{ color: "blue" }}>
                  <b>Experience Required:</b> {job.experience} years
                </Typography>
              </Box>
            ))
          )}
        </Box>
      </Box>
    );
  }

  if (message.type === "interview_list") {
    const interviews = message.interviews || [];

    return (
      <Box sx={{ display: "flex", flexDirection: "column" }}>
        <Box sx={bubbleStyle}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            📅 Interview List
          </Typography>

          {interviews.length === 0 ? (
            <Typography>No interviews scheduled</Typography>
          ) : (
            interviews.map((item, i) => (
              <Box
                key={i}
                sx={{
                  border: "1px solid #ccc",
                  borderRadius: 2,
                  p: 2,
                  mt: 1.5,
                  backgroundColor: "#fff",
                  color: "#000"
                }}
              >
                <Typography sx={{ mb: 0.5 }}>
                  <b>Interviewer Name:</b> {item.interviewer_name}
                </Typography>

                <Typography sx={{ mb: 0.5 }}>
                  <b>Candidate Name:</b> {item.candidate_name}
                </Typography>

                <Typography sx={{ mb: 0.5 }}>
                  <b>Job Role:</b> {item.job_role}
                </Typography>

                <Typography sx={{ mb: 0.5 }}>
                  <b>Interview Date:</b> {item.interview_date}
                </Typography>

                <Typography sx={{ color: "blue" }}>
                  <b>Status:</b> {item.interview_status}
                </Typography>
              </Box>
            ))
          )}
        </Box>
      </Box>
    );
  }

  return null;
}