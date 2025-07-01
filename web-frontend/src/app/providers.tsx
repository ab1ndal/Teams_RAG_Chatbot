// app/providers.tsx
"use client";

import { MantineProvider } from "@mantine/core";
import { ReactNode } from "react";

export default function Providers({ children }: { children: ReactNode }) {
  return (
    <MantineProvider
      defaultColorScheme="light"
      theme={{
        fontFamily: "var(--font-geist-sans), sans-serif",
        headings: { fontFamily: "var(--font-geist-sans), sans-serif" },
        primaryColor: "blue",
        defaultRadius: "md",
      }}
    >
      {children}
    </MantineProvider>
  );
}
