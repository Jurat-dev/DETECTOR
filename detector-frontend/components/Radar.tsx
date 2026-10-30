"use client";
import { motion } from "framer-motion";

export default function Radar({ size = 40, scanning = true, speed = 2.4 }: { size?: number; scanning?: boolean; speed?: number }) {
  return (
    <div className="relative rounded-full shrink-0" style={{ width: size, height: size, background: "radial-gradient(circle, rgba(63,208,212,.14), rgba(4,20,35,.6) 70%)", border: "1.5px solid rgba(63,208,212,.7)", boxShadow: "0 0 24px rgba(63,208,212,.35), inset 0 0 18px rgba(63,208,212,.2)" }}>
      {[0.66, 0.33].map((s) => (
        <div key={s} className="absolute rounded-full border border-turq/40" style={{ inset: `${((1 - s) / 2) * 100}%` }} />
      ))}
      <div className="absolute left-1/2 top-0 bottom-0 w-px bg-turq/25" />
      <div className="absolute top-1/2 left-0 right-0 h-px bg-turq/25" />
      {scanning && (
        <motion.div className="absolute inset-0 rounded-full" style={{ background: "conic-gradient(from 0deg, rgba(63,208,212,0) 0deg, rgba(63,208,212,0) 280deg, rgba(63,208,212,.75) 360deg)" }}
          animate={{ rotate: 360 }} transition={{ repeat: Infinity, ease: "linear", duration: speed }} />
      )}
      {scanning && [[0.68, 0.3], [0.3, 0.62], [0.58, 0.72]].map(([l, t], i) => (
        <motion.span key={i} className="absolute rounded-full bg-gold" style={{ left: `${l * 100}%`, top: `${t * 100}%`, width: Math.max(3, size / 28), height: Math.max(3, size / 28), boxShadow: "0 0 8px #e8c26a" }}
          animate={{ opacity: [0, 1, 0] }} transition={{ repeat: Infinity, duration: speed, delay: (i * speed) / 3 }} />
      ))}
      <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-turq" style={{ width: Math.max(3, size / 16), height: Math.max(3, size / 16) }} />
    </div>
  );
}
