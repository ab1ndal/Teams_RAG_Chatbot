import React from "react";
import { ScrollArea } from "@/components/ui/scroll-area";

const ChatWindow = ({ messages }) => (
  <ScrollArea className="flex-1 p-4 space-y-4 overflow-y-auto">
    {messages.map((msg, i) => (
      <div
        key={i}
        className={`max-w-lg px-4 py-2 rounded-xl ${
          msg.role === "user" ? "ml-auto bg-primary text-white" : "mr-auto bg-muted"
        }`}
      >
        {msg.content}
      </div>
    ))}
  </ScrollArea>
);

export default ChatWindow;
