import React from "react";

const ThreadItem = ({ thread, onClick }) => (
  <div
    className="cursor-pointer p-2 rounded hover:bg-muted transition"
    onClick={onClick}
  >
    {thread.title || thread.id}
  </div>
);

export default ThreadItem;
