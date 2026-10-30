"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import { useState } from "react";

const theme = createTheme({
  palette: { mode: "dark", primary: { main: "#3fd0d4" }, secondary: { main: "#e8c26a" }, background: { default: "transparent", paper: "rgba(10,30,50,.6)" } },
  typography: { fontFamily: "var(--font-inter), Inter, sans-serif" },
  shape: { borderRadius: 14 },
});

export default function Providers({ children }: { children: React.ReactNode }) {
  const [qc] = useState(() => new QueryClient({ defaultOptions: { queries: { staleTime: 60_000, retry: 1, refetchOnWindowFocus: false } } }));
  return (
    <QueryClientProvider client={qc}>
      <ThemeProvider theme={theme}>
        <CssBaseline enableColorScheme />
        {children}
      </ThemeProvider>
    </QueryClientProvider>
  );
}
