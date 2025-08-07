// src/components/ChatWindow.tsx
import { useChat } from "@/context/ChatContext";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";

export default function ChatWindow() {
  const { messages } = useChat();

  return (
    <ScrollArea className="flex-1 flex flex-col gap-4 pr-2">
      {messages.length === 0 ? (
        <div className="text-sm text-gray-400 text-center mt-8">
          This thread is empty. Start the conversation below ⤵️
        </div>
      ) : (
        messages.map((msg) => (
          <div key={msg.id} className="mb-4">
            <div
              className={`max-w-xl px-4 py-3 rounded-lg shadow-sm text-sm ${
                msg.role === "user"
                  ? "bg-amber-100 self-end ml-auto"
                  : "bg-white border self-start"
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <Badge
                  variant="outline"
                  className={`text-xs ${
                    msg.role === "user"
                      ? "border-amber-600 text-amber-700"
                      : "border-gray-400 text-gray-700"
                  }`}
                >
                  {msg.role === "user" ? "You" : "Assistant"}
                </Badge>
                <span className="text-[10px] text-gray-400 ml-auto">
                  {new Date(msg.created_at).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-gray-800 whitespace-pre-wrap">{msg.content}</p>
            </div>
          </div>
        ))
      )}
    </ScrollArea>
  );
}
