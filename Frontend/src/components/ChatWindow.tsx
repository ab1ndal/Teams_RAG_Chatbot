// src/components/ChatWindow.tsx
import { useChat } from "@/context/ChatContext";
import { ScrollArea } from "@/components/ui/scroll-area";
import AnswerCard from "@/components/AnswerCard";

export default function ChatWindow() {
  const { messages, isLoading, isError } = useChat();

  return (
    <ScrollArea className="flex-1 flex flex-col gap-4 pr-2">
      {messages.length === 0 ? (
        <div className="text-sm text-gray-400 text-center mt-8">
          This thread is empty. Start the conversation below ⤵️
        </div>
      ) : (
        <>
        {messages.map((msg) => (
          <div key={msg.id} className="mb-4">
            <AnswerCard
              role={msg.role}
              content={msg.content}
              createdAt={msg.created_at}
              images={msg.images}
            />
          </div>
        ))}
        {isLoading && (
            <div className="mb-4">
              <AnswerCard
                role="assistant"
                content=""
                createdAt={new Date().toISOString()}
                isLoading
              />
            </div>
          )}
          {isError && (
            <div className="mb-4">
              <AnswerCard
                role="system"
                content=""
                createdAt={new Date().toISOString()}
                isError
              />
            </div>
          )}
        </>
      )}
    </ScrollArea>
  );
}
