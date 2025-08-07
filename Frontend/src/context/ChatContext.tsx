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
    const { data: contextMessages, error: fetchErr } = await supabase
    .from("messages")
    .select("role, content")
    .eq("thread_id", selectedThread.id)
    .order("created_at", { ascending: true });

    if (fetchErr || !contextMessages) {
    toast.error("Failed to fetch thread context");
    return;
    }

    // 2. Call your FastAPI backend
    const response = await fetch("http://localhost:8000/generate", {
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
    setMessages((prev) => [...prev, aiMsg[0]]);
    } else {
    toast.error("Failed to get AI response");
    }
    };
  
    return (
      <ChatContext.Provider
        value={{
          selectedThread,
          setSelectedThread,
          messages,
          sendMessage,
        }}
      >
        {children}
      </ChatContext.Provider>
    );
  };
  