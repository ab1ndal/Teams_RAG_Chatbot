import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabaseClient";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { v4 as uuidv4 } from "uuid";
import { toast } from "sonner";

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
    console.log("handleTitleChange", id, title);
    const existing = threads.find((t) => t.id === id);
    if (!existing || existing.title === title) {
      setEditingId(null);
      return;
    }

    const { data, error } = await supabase
      .from("threads")
      .update({ title })
      .eq("id", id)
      .select();

    console.log("handleTitleChange", error);
    console.log(data);

    if (error) {
      toast.error("Failed to update title", { description: error.message });
    } else {
      setThreads((prev) =>
        prev.map((t) => (t.id === id ? { ...t, title } : t))
      );
    }
    setEditingId(null);
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
              onClick={() => onSelect(thread)}
              onDoubleClick={() => setEditingId(thread.id)}
              className={`cursor-pointer px-3 py-2 text-sm rounded hover:bg-muted ${
                selectedThreadId === thread.id ? "bg-muted font-medium" : ""
              }`}
            >
              {thread.title || "Untitled"}
            </div>
          )
        )}
      </div>
    </div>
  );
}
