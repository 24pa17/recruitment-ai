import { Box, Button } from "@mui/material";

export default function SuggestionButtons({ onClick }) {
  return (
    <Box sx={{ mt: 2 }}>
      <Button onClick={() => onClick("Show job openings")} sx={{ mr: 1 }} variant="outlined">Job Openings</Button>
      <Button onClick={() => onClick("Find candidates for Python role")} sx={{ mr: 1 }} variant="outlined">Find Candidates</Button>
      <Button onClick={() => onClick("Interview schedule")} sx={{ mr: 1 }} variant="outlined">Interviews</Button>
      
    </Box>
  );
}
