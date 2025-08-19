// src/components/ChatWindow.tsx
import { useChat } from "@/context/ChatContext";
import { ScrollArea } from "@/components/ui/scroll-area";
import AnswerCard from "@/components/AnswerCard";
import { useEffect, useRef } from "react";

export default function ChatWindow() {
  const { messages, isLoading, isError } = useChat();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // scroll to bottom on first mount and whenever messages/loading change
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages.length, isLoading, isError]);

  return (
    <ScrollArea className="h-full pr-2">
      <div className="flex flex-col gap-4">
      {messages.length === 0 ? (
        <div className="text-sm text-gray-400 text-center mt-8">
          This thread is empty. Start the conversation below ⤵️
        </div>
      ) : (
        <>
        {messages.map((msg) => (
          <div key={msg.id} className="mb-1">
            <AnswerCard
              role={msg.role}
              content={msg.content}
              createdAt={msg.created_at}
              images={msg.images}
            />
          </div>
        ))}
        {isLoading && (
            <div className="mb-1">
              <AnswerCard
                role="assistant"
                content=""
                createdAt={new Date().toISOString()}
                isLoading
              />
            </div>
          )}
          {isError && (
            <div className="mb-1">
              <AnswerCard
                role="system"
                content=""
                createdAt={new Date().toISOString()}
                isError
              />
            </div>
          )}
          <div ref={bottomRef} />
        </>
      )}
      </div>
    </ScrollArea>
  );
}
