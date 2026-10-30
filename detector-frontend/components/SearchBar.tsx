"use client";
import { InputBase, Button } from "@mui/material";
import { useState, useEffect } from "react";

export default function SearchBar({ initial = "", onSearch, loading }: { initial?: string; onSearch: (q: string) => void; loading?: boolean }) {
  const [q, setQ] = useState(initial);
  useEffect(() => setQ(initial), [initial]);
  return (
    <form onSubmit={(e) => { e.preventDefault(); if (q.trim()) onSearch(q.trim()); }} className="glass flex items-center gap-3 px-5 py-2.5 w-full">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3fd0d4" strokeWidth="2"><circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" /></svg>
      <InputBase value={q} onChange={(e) => setQ(e.target.value)} placeholder="So‘z yoki iborani yozing… (masalan: mehr-u oqibat)" fullWidth
        sx={{ color: "#eef6f8", fontSize: 18, "& input::placeholder": { color: "#9fb6c1", opacity: 1 } }} inputProps={{ "aria-label": "Qidiruv" }} />
      <Button type="submit" variant="contained" disabled={loading} sx={{ px: 3.5, py: 1.2, fontWeight: 700, textTransform: "none", borderRadius: "12px", background: "linear-gradient(90deg,#1fb5c0,#2e7fd6)", color: "#fff", whiteSpace: "nowrap" }}>
        {loading ? "Skanerlanmoqda…" : "Qidirish"}
      </Button>
    </form>
  );
}
