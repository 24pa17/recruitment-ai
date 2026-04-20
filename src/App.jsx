import ChatBot from "./components/ChatBot";
import { Box } from "@mui/material";

function App() {
  return (
    <Box sx={{ display: "flex", height: "100vh", background: "#f5f7fb" }}>
      <ChatBot />
    </Box>
  );
}

export default App;