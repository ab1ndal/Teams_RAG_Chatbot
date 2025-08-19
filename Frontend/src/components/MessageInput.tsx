import { useState, useEffect, useRef } from "react";
import { useChat } from "@/context/ChatContext";
import { Button } from "@/components/ui/button";
// If you have shadcn's Textarea component, prefer this:
import { Textarea } from "@/components/ui/textarea";

export default function MessageInput() {
  const [content, setContent] = useState("");
  const { sendMessage } = useChat();
  const ref = useRef<HTMLTextAreaElement>(null);
  const MAX_HEIGHT = 200; // px cap so it doesn't take over the screen

  const autoResize = () => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, MAX_HEIGHT) + "px";
  };

  useEffect(() => {
    autoResize();
  }, [content]);

  const handleSend = async () => {
    const text = content.trim();
    if (!text) return;
    await sendMessage(text);
    setContent("");
    requestAnimationFrame(autoResize);
  };

  return (
    <div className="flex items-end gap-2">
      <div className="flex-1">
        <Textarea
          ref={ref}
          rows={1}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onInput={autoResize}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault(); // prevent newline
              handleSend();
            }
          }}
          placeholder="Type your message…"
          className="resize-none overflow-hidden"
        />
      </div>
      <Button onClick={handleSend} disabled={!content.trim()}>
        Send
      </Button>
    </div>
  );
}
