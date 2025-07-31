import React, { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

const MessageInput = ({ onSend }) => {
  const [value, setValue] = useState("");

  const handleSend = () => {
    if (value.trim()) {
      onSend(value);
      setValue("");
    }
  };

  return (
    <div className="flex p-4 border-t gap-2">
      <Input
        placeholder="Type your message..."
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
      />
      <Button onClick={handleSend}>Send</Button>
    </div>
  );
};

export default MessageInput;
