"use client";
import { motion } from "framer-motion";
import Link from "next/link";
import Radar from "./Radar";

export default function Logo({ scanning = false }: { scanning?: boolean }) {
  return (
    <Link href="/" className="flex items-center gap-3 font-extrabold text-2xl tracking-wide">
      <motion.div layoutId="detector-radar" transition={{ type: "spring", stiffness: 70, damping: 16 }}>
        <Radar size={40} scanning={scanning} speed={1.6} />
      </motion.div>
      <motion.span className="brand" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 }}>Detector</motion.span>
    </Link>
  );
}
