// src/context/ChatContext.tsx
import {
    createContext,
    useContext,
    useState,
    useEffect,
  } from "react";
  import { supabase } from "@/lib/supabaseClient";
  import { toast } from "sonner";
  
  type Message = {
    id: string;
    thread_id: string;
    user_id: string | null;
    role: "user" | "assistant";
    content: string | null;
    created_at: string;
    images?: string[];
  };
  
  type Thread = {
    id: string;
    title: string | null;
    created_at: string;
  };
  
  type ChatContextType = {
    selectedThread: Thread | null;
    setSelectedThread: (thread: Thread | null) => void;
    messages: Message[];
    sendMessage: (content: string) => Promise<void>;
    isLoading: boolean;
    isError: boolean;
  };
  
  const ChatContext = createContext<ChatContextType | null>(null);
  
  export const useChat = () => {
    const ctx = useContext(ChatContext);
    if (!ctx) throw new Error("useChat must be used within ChatProvider");
    return ctx;
  };
  
  export const ChatProvider = ({ children }: { children: React.ReactNode }) => {
    const [selectedThread, setSelectedThread] = useState<Thread | null>(null);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isError, setIsError] = useState(false);

    useEffect(() => {
      const fetchMessages = async () => {
        if (!selectedThread) return;
  
        const { data, error } = await supabase
          .from("messages")
          .select("*")
          .eq("thread_id", selectedThread.id)
          .order("created_at", { ascending: true });
  
        if (!error && data) {
          setMessages(data as Message[]);
        }
      };
  
      fetchMessages();
    }, [selectedThread]);
  
    const sendMessage = async (content: string) => {
      if (!selectedThread) return;
  
      const {
        data: { user },
      } = await supabase.auth.getUser();
  
      // Insert user message
      const { data: userMsg, error: userErr } = await supabase
        .from("messages")
        .insert([
          {
            thread_id: selectedThread.id,
            user_id: user?.id,
            role: "user",
            content,
          },
        ])
        .select();
  
      if (userErr || !userMsg) {
        toast.error("Failed to send message");
        return;
      }
  
      const userMessage = userMsg[0];
      setMessages((prev) => [...prev, userMessage]);
  
    // 1. Fetch full thread context
    const contextMessages = [
    ...messages.map((m) => ({ role: m.role, content: m.content })),
    { role: "user", content },
    ];

    // Set loading state
    setIsLoading(true);
    setIsError(false);

    // 2. Call your FastAPI backend
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
      user_id: user?.id,
      thread_id: selectedThread.id,
      messages: contextMessages,
      }),
    });

    const result = await response.json();
    const aiResponse = result.final_answer ?? "[No response]";
    const plotImages: string[] = result.plot_images ?? [];

    // 3. Insert assistant message
    const { data: aiMsg, error: aiErr } = await supabase
    .from("messages")
    .insert([
    {
        thread_id: selectedThread.id,
        user_id: user?.id,
        role: "assistant",
        content: aiResponse,
    },
    ])
    .select();

    if (!aiErr && aiMsg) {
      const enriched = {
        ...aiMsg[0],
        images: plotImages,
      }
      setMessages((prev) => [...prev, enriched]);
    } else {
      setIsError(true);
      toast.error("Failed to get AI response");
    }
    } catch (error) {
      console.error("Error getting AI response:", error);
      setIsError(true);
      toast.error("Failed to get AI response");
    } finally {
      setIsLoading(false);
    }
    };
  
    return (
      <ChatContext.Provider
        value={{
          selectedThread,
          setSelectedThread,
          messages,
          sendMessage,
          isLoading,
          isError,
        }}
      >
        {children}
      </ChatContext.Provider>
    );
  };
  