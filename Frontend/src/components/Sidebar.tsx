import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { v4 as uuidv4 } from "uuid";
import { toast } from "sonner";
import {Trash2} from "lucide-react"

type Thread = {
  id: string;
  title: string | null;
  created_at: string;
};

export default function Sidebar({
  onSelect,
  selectedThreadId,
}: {
  onSelect: (thread: Thread) => void;
  selectedThreadId: string | null;
}) {
  const [threads, setThreads] = useState<Thread[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const fetchThreads = async () => {
      const {
        data: { user },
      } = await supabase.auth.getUser();

      if (!user) return;

      setUserId(user.id);

      const { data, error } = await supabase
        .from("threads")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", { ascending: false });

      if (error) {
        toast.error("Failed to fetch threads", { description: error.message });
        return;
      }

      setThreads(data);
    };

    fetchThreads();
  }, []);

  const createThread = async () => {
    if (!userId) return;

    const newId = uuidv4();
    const newThread: Thread = {
      id: newId,
      title: "New Chat",
      created_at: new Date().toISOString(),
    };

    const { error } = await supabase.from("threads").insert({
      id: newId,
      user_id: userId,
      title: newThread.title,
    });

    if (error) {
      toast.error("Error creating thread", { description: error.message });
      return;
    }

    setThreads((prev) => [newThread, ...prev]);
    onSelect(newThread);
  };

  const handleTitleChange = async (id: string, title: string) => {
    const existing = threads.find((t) => t.id === id);
    if (!existing || existing.title === title) {
      setEditingId(null);
      return;
    }

    const { error } = await supabase
      .from("threads")
      .update({ title })
      .eq("id", id);

    if (error) {
      toast.error("Failed to update title", { description: error.message });
    } else {
      setThreads((prev) =>
        prev.map((t) => (t.id === id ? { ...t, title } : t))
      );
    }
    setEditingId(null);
  };

  const deleteThread = async (threadId: string) => {
    //Confirm deletion
    const confirmed = window.confirm("Are you sure you want to delete this conversation?");
    if (!confirmed) return;

    // Delete messages in the thread
    const {error: messageDeleteError } = await supabase
      .from("messages")
      .delete()
      .eq("thread_id", threadId);
    if (messageDeleteError) {
      toast.error("Failed to delete Thread", { description: messageDeleteError?.message || "Failed to delete thread" });
      return;
    }

    // Delete thread
    const {error: threadDeleteError } = await supabase
      .from("threads")
      .delete()
      .eq("id", threadId);
    
    if (threadDeleteError) {
      toast.error("Failed to delete thread", { description: threadDeleteError?.message || "Failed to delete thread" });
      return;
    }

    setThreads((prev) => prev.filter((t) => t.id !== threadId));
    toast.success("Conversation deleted successfully");

    if (selectedThreadId === threadId) {
      onSelect({id: "", title: null, created_at: ""});
    }
  };

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-md font-semibold">Conversations</h3>
        <Button
          size="sm"
          className="text-xs bg-amber-600 hover:bg-amber-700"
          onClick={createThread}
        >
          + New
        </Button>
      </div>

      <div className="space-y-2 overflow-y-auto flex-1 pr-2">
        {threads.map((thread) =>
          editingId === thread.id ? (
            <Input
              key={thread.id}
              autoFocus
              className="text-sm"
              defaultValue={thread.title ?? ""}
              onBlur={(e) => handleTitleChange(thread.id, e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  (e.target as HTMLInputElement).blur();
                }
              }}
            />
          ) : (
            <div
              key={thread.id}
              className={`group flex items-center justify-between cursor-pointer px-3 py-2 text-sm rounded hover:bg-muted ${
                selectedThreadId === thread.id ? "bg-muted font-medium" : ""
              }`}
            >
              <div
                className="flex-1 truncate"
                onClick={() => onSelect(thread)}
                onDoubleClick={() => setEditingId(thread.id)}
              >
                {thread.title || "Untitled"}
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation(); // Prevent click from selecting the thread
                  deleteThread(thread.id);
                }}
                className="ml-2 text-muted-foreground hover:text-red-600 p-1"
              >
                <Trash2 size={16} />
              </button>
            </div>
          )
        )}
      </div>
    </div>
  );
}
