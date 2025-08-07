import { useState } from "react";
import { useChat } from "@/context/ChatContext";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function MessageInput() {
  const [content, setContent] = useState("");
  const { sendMessage } = useChat();

  const handleSend = async () => {
    if (!content.trim()) return;
    await sendMessage(content);
    setContent("");
  };

  return (
    <div className="mt-2 flex gap-2">
      <Input
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Type your message..."
        onKeyDown={(e) => {
          if (e.key === "Enter") handleSend();
        }}
      />
      <Button onClick={handleSend}>Send</Button>
    </div>
  );
}
