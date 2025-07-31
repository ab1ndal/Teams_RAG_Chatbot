import React, { useState, useEffect } from "react";
import { fetchThreads, fetchMessages, sendMessage, createThread } from "../api/backend";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import MessageInput from "../components/MessageInput";
import { Button } from "@/components/ui/button";

const ChatPage = () => {
  const [userId] = useState("user-123"); // from auth
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null);
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    fetchThreads(userId).then(setThreads);
  }, [userId]);

  const handleSelectThread = async (thread) => {
    setSelectedThread(thread);
    const msgs = await fetchMessages(thread.id);
    setMessages(msgs);
  };

  const handleSend = async (text) => {
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    const response = await sendMessage({ userId, threadId: selectedThread.id, message: text });
    setMessages((prev) => [...prev, { role: "assistant", content: response.answer }]);
  };

  return (
    <div className="flex h-screen">
      <Sidebar threads={threads} onSelect={handleSelectThread} />
      <div className="flex flex-col flex-1">
        <div className="flex justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">{selectedThread?.title || "Chat"}</h2>
          <Button
            onClick={async () => {
              const newThreadId = `thread_${Date.now()}`;
              await createThread({ userId, threadId: newThreadId, title: "New Chat" });
              const thread = { id: newThreadId, title: "New Chat" };
              setThreads([thread, ...threads]);
              handleSelectThread(thread);
            }}
          >
            + New Chat
          </Button>
        </div>
        <ChatWindow messages={messages} />
        <MessageInput onSend={handleSend} />
      </div>
    </div>
  );
};

export default ChatPage;
