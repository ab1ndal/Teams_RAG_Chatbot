import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import Sidebar from "@/components/Sidebar";
import ChatWindow from "@/components/ChatWindow";
import MessageInput from "@/components/MessageInput";
import { ChatProvider, useChat } from "@/context/ChatContext";

function ChatContent() {
  const { selectedThread, setSelectedThread } = useChat();

  return (
    <div className="flex flex-1 overflow-hidden">
      {/* Sidebar */}
      <div className="w-1/4 bg-muted border-r overflow-y-auto p-4">
        <Sidebar
          onSelect={(thread) => setSelectedThread(thread)}
          selectedThreadId={selectedThread?.id || null}
        />
      </div>

      {/* Chat area */}
      <div className="w-3/4 p-6 flex flex-col overflow-hidden">
        {selectedThread ? (
          <>
            <ChatWindow />
            <MessageInput />
          </>
        ) : (
          <div className="text-gray-500 text-sm">
            Select a thread to start chatting
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [firstName, setFirstName] = useState<string | null>(null);
  const [lastName, setLastName] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const getUser = async () => {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (user) {
        const { data: userData } = await supabase
          .from("users")
          .select("*")
          .eq("id", user.id)
          .single();
        if (userData) {
          setFirstName(userData.first_name || null);
          setLastName(userData.last_name || null);
        }
      }
    };

    getUser();
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate("/login");
  };

  return (
    <ChatProvider>
      <div className="min-h-screen flex flex-col">
        {/* Top menu bar */}
        <div className="flex items-center justify-between bg-amber-600 text-white px-6 py-3 shadow">
          <div className="text-lg font-semibold">NYA Chatbot</div>
          <div className="flex items-center gap-4">
            <span className="text-sm">
              {firstName} {lastName}
            </span>
            <Button
              variant="outline"
              className="text-white border-white hover:bg-white hover:text-amber-600 transition"
              onClick={handleLogout}
            >
              Logout
            </Button>
          </div>
        </div>

        {/* Main content */}
        <ChatContent />
      </div>
    </ChatProvider>
  );
}
