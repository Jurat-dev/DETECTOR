"use client";
import { motion } from "framer-motion";
import type { BookResult } from "@/lib/api";

export const cardVariants = { hidden: { opacity: 0, y: 28, scale: 0.97 }, show: { opacity: 1, y: 0, scale: 1, transition: { type: "spring" as const, stiffness: 120, damping: 18 } } };

export default function ResultCard({ r, onOpen }: { r: BookResult; onOpen: (r: BookResult, page?: number) => void }) {
  return (
    <motion.div variants={cardVariants} layoutId={`card-${r.book.id}`} whileHover={{ y: -4, boxShadow: "0 14px 50px rgba(63,208,212,.25)" }}
      onClick={() => onOpen(r)} className="glass p-5 cursor-pointer flex flex-col gap-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-bold">{r.book.title}</h3>
          {r.book.author && <p className="text-sm text-[#9fb6c1]">{r.book.author}</p>}
        </div>
        <div className="text-right">
          <div className="text-2xl font-extrabold text-gold">{r.count}</div>
          <div className="text-[11px] text-[#9fb6c1]">moslik · {r.pages} bet</div>
        </div>
      </div>
      <div className="flex gap-2 flex-wrap">
        {r.exact_count > 0 && <span className="tag">aniq: {r.exact_count}</span>}
        {r.forms_count > 0 && <span className="tag tag-gold">so‘z shakllari: {r.forms_count}</span>}
        {r.book.source_type !== "text" && <span className="tag">OCR</span>}
      </div>
      <ul className="flex flex-col gap-2">
        {r.snippets.map((s, i) => (
          <li key={i} onClick={(e) => { e.stopPropagation(); onOpen(r, s.page); }} className="text-sm leading-relaxed text-[#cfe0e6] rounded-lg px-3 py-2 bg-white/5 hover:bg-white/10 transition">
            <span className="text-turq text-xs font-semibold mr-2">{s.page}-bet</span>
            {s.before}<mark>{s.highlight}</mark>{s.after}
          </li>
        ))}
      </ul>
    </motion.div>
  );
}
