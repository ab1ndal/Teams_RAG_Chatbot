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
    <div className="h-full grid grid-cols-[1fr,3fr] overflow-hidden">
      {/* Sidebar column: let Sidebar manage its own scroll */}
      <aside className="min-h-0 overflow-y-auto border-r bg-muted/20 p-4">
        <Sidebar
          onSelect={(thread) => setSelectedThread(thread)}
          selectedThreadId={selectedThread?.id || null}
        />
      </aside>

      {/* Chat column */}
      <main className="min-h-0 flex flex-col p-6">
        {selectedThread ? (
          <>
            {/* Messages area: the ONLY scroll on the right */}
            <div className="flex-1 min-h-0 overflow-y-auto">
              <ChatWindow />
            </div>

            {/* Input bar: outside the scroll, always visible */}
            <div className="border-t pt-3 bg-background">
              <MessageInput />
            </div>
          </>
        ) : (
          <div className="text-gray-500 text-sm">Select a thread to start chatting</div>
        )}
      </main>
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
      <div className="h-screen flex flex-col">
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

        {/* Main content must consume remaining height */}
        <div className="flex-1 min-h-0 overflow-hidden">
          <ChatContent />
        </div>
      </div>
    </ChatProvider>
  );
}
