"use client";
import { AnimatePresence, motion } from "framer-motion";
import { useMutation } from "@tanstack/react-query";
import { InputBase, IconButton } from "@mui/material";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import Radar from "./Radar";
import { api, type Source } from "@/lib/api";

type Msg = { role: "user" | "bot"; text: string; sources?: Source[] };

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([{ role: "bot", text: "Salom! Kitoblar bo‘yicha savol bering — faqat kitob matnidan, manbasi bilan javob beraman." }]);
  const [q, setQ] = useState("");
  const router = useRouter();
  const end = useRef<HTMLDivElement>(null);
  const mut = useMutation({
    mutationFn: api.chat,
    onSuccess: (r) => setMsgs((m) => [...m, { role: "bot", text: r.answer, sources: r.sources }]),
    onError: () => setMsgs((m) => [...m, { role: "bot", text: "Serverga ulanib bo‘lmadi." }]),
  });
  useEffect(() => end.current?.scrollIntoView({ behavior: "smooth" }), [msgs, mut.isPending]);
  const send = () => { const t = q.trim(); if (!t || mut.isPending) return; setMsgs((m) => [...m, { role: "user", text: t }]); setQ(""); mut.mutate(t); };

  return (
    <>
      <motion.button aria-label="Chatbotni ochish" onClick={() => setOpen((o) => !o)} whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.95 }}
        className="fixed bottom-6 right-6 z-50 rounded-full" style={{ boxShadow: "0 0 30px rgba(63,208,212,.45)" }}>
        <Radar size={64} speed={open ? 1 : 3} />
      </motion.button>
      <AnimatePresence>
        {open && (
          <motion.aside initial={{ x: 440, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: 440, opacity: 0 }} transition={{ type: "spring", stiffness: 140, damping: 20 }}
            className="glass fixed right-4 top-4 bottom-28 z-50 w-[min(420px,calc(100vw-2rem))] flex flex-col !rounded-2xl">
            <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
              <div className="flex items-center gap-3"><Radar size={28} speed={1.5} scanning={mut.isPending} /><b>Detector yordamchisi</b></div>
              <IconButton onClick={() => setOpen(false)} size="small" sx={{ color: "#b9cdd6" }} aria-label="Yopish">✕</IconButton>
            </div>
            <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3">
              {msgs.map((m, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className={`max-w-[88%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${m.role === "user" ? "self-end bg-turq/20 border border-turq/40" : "self-start bg-white/7 border border-white/10"}`}>
                  {m.text}
                  {m.sources && m.sources.length > 0 && (
                    <div className="mt-3 flex flex-col gap-1.5">
                      <span className="text-xs text-gold font-semibold">Manbalar:</span>
                      {m.sources.map((s) => (
                        <button key={s.n} onClick={() => router.push(`/book/${s.book_id}?page=${s.page}`)} className="text-left text-xs rounded-lg px-2.5 py-1.5 bg-white/5 hover:bg-turq/15 transition">
                          <span className="text-turq font-semibold">[{s.n}]</span> {s.title} · {s.page}-bet{s.approximate && <span className="text-gold"> (taxminiy)</span>}
                        </button>
                      ))}
                    </div>
                  )}
                </motion.div>
              ))}
              {mut.isPending && <div className="self-start text-sm text-turq">Kitoblar skanerlanmoqda…</div>}
              <div ref={end} />
            </div>
            <form onSubmit={(e) => { e.preventDefault(); send(); }} className="flex items-center gap-2 p-3 border-t border-white/10">
              <InputBase value={q} onChange={(e) => setQ(e.target.value)} placeholder="Savolingizni yozing…" fullWidth sx={{ color: "#eef6f8", px: 1.5 }} />
              <button type="submit" className="rounded-xl px-4 py-2 font-semibold text-white" style={{ background: "linear-gradient(90deg,#1fb5c0,#2e7fd6)" }}>Yuborish</button>
            </form>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}
