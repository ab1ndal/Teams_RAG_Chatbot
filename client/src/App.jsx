import React from "react";
import { Routes, Route } from "react-router-dom";
import ChatPage from "./routes/ChatPage";

const App = () => {
  return (
    <Routes>
      <Route path="/" element={<ChatPage />} />
    </Routes>
  );
};

export default App;
