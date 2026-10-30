"use client";
import { motion, useMotionValue, useSpring, useTransform } from "framer-motion";
import { useEffect } from "react";

export default function Background() {
  const mx = useMotionValue(0), my = useMotionValue(0);
  const sx = useSpring(mx, { stiffness: 40, damping: 18 }), sy = useSpring(my, { stiffness: 40, damping: 18 });
  const x = useTransform(sx, (v) => v * -18), y = useTransform(sy, (v) => v * -12);
  useEffect(() => {
    const on = (e: MouseEvent) => { mx.set(e.clientX / window.innerWidth - 0.5); my.set(e.clientY / window.innerHeight - 0.5); };
    window.addEventListener("mousemove", on);
    return () => window.removeEventListener("mousemove", on);
  }, [mx, my]);
  return (
    <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none" aria-hidden>
      <motion.div style={{ x, y, backgroundImage: "url(/registon.jpg)" }} className="absolute -inset-10 bg-cover bg-center blur-[3px] scale-105" />
      <div className="absolute inset-0" style={{ background: "linear-gradient(180deg,rgba(4,16,30,.72),rgba(5,22,40,.86))" }} />
    </div>
  );
}
