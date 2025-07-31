import React from "react";
import ThreadItem from "./ThreadItem";

const Sidebar = ({ threads, onSelect }) => (
  <div className="w-64 bg-muted border-r h-full p-4 overflow-y-auto">
    <h3 className="text-md font-semibold mb-4">Conversations</h3>
    <div className="space-y-2">
      {threads.map((t) => (
        <ThreadItem key={t.id} thread={t} onClick={() => onSelect(t)} />
      ))}
    </div>
  </div>
);

export default Sidebar;
