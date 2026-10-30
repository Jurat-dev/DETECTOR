"use client";
import { Suspense, useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Button } from "@mui/material";
import Logo from "@/components/Logo";
import Radar from "@/components/Radar";
import { api } from "@/lib/api";

const PdfViewer = dynamic(() => import("@/components/PdfViewer"), { ssr: false });

function BookView() {
  const { id } = useParams<{ id: string }>();
  const bookId = Number(id);
  const sp = useSearchParams();
  const router = useRouter();
  const q = sp.get("q") || "";
  const startPage = Number(sp.get("page") || 0);

  const book = useQuery({ queryKey: ["book", bookId], queryFn: () => api.book(bookId) });
  const m = useQuery({ queryKey: ["matches", bookId, q], queryFn: () => api.matches(bookId, q), enabled: !!q });
  const matches = useMemo(() => m.data?.matches ?? [], [m.data]);
  const [idx, setIdx] = useState(0);
  const [page, setPage] = useState(startPage || 1);
  const [numPages, setNumPages] = useState(0);

  useEffect(() => {
    if (!matches.length) return;
    const i = startPage ? Math.max(0, matches.findIndex((x) => x.page === startPage)) : 0;
    setIdx(i); setPage(matches[i].page);
  }, [matches, startPage]);

  const go = (i: number) => { if (i < 0 || i >= matches.length) return; setIdx(i); setPage(matches[i].page); };
  const cur = matches[idx];
  const boxes = cur && cur.page === page ? matches.filter((x) => x.page === page).flatMap((x) => x.bbox) : [];

  return (
    <div className="min-h-screen flex flex-col">
      <header className="grid grid-cols-[1fr_auto_1fr] items-center px-6 md:px-12 py-5 gap-4">
        <Logo />
        <div className="text-center">
          <h1 className="text-xl font-bold">{book.data?.title ?? "…"}</h1>
          <p className="text-xs text-turq">{book.data?.author}{q && <> · «{q}» — {matches.length} ta moslik</>}</p>
        </div>
        <div className="flex justify-end">
          <Button onClick={() => (q ? router.push(`/?q=${encodeURIComponent(q)}`) : router.push("/"))} className="glass" sx={{ textTransform: "none", color: "#eef6f8", borderRadius: "99px", px: 2.5 }}>← Natijalarga qaytish</Button>
        </div>
      </header>

      <div className="flex-1 grid md:grid-cols-[320px_1fr] gap-6 px-6 md:px-12 pb-8">
        <motion.aside initial={{ x: -40, opacity: 0 }} animate={{ x: 0, opacity: 1 }} className="glass p-4 md:h-[calc(100vh-120px)] overflow-y-auto">
          <h2 className="text-gold font-bold text-sm tracking-wider mb-3">MOSLIKLAR ({matches.length})</h2>
          {m.isFetching && <div className="flex justify-center py-8"><Radar size={70} speed={1} /></div>}
          {!q && <p className="text-sm text-[#9fb6c1]">Qidiruv so‘zi berilmagan.</p>}
          {q && !m.isFetching && matches.length === 0 && <p className="text-sm text-[#9fb6c1]">Bu kitobda moslik topilmadi.</p>}
          <ul className="flex flex-col gap-1.5">
            {matches.map((x, i) => (
              <motion.li key={x.index} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: Math.min(i, 20) * 0.03 }}
                onClick={() => go(i)} className={`cursor-pointer rounded-xl px-3 py-2 text-sm border transition ${i === idx ? "bg-turq/15 border-turq/50" : "border-transparent hover:bg-white/5"}`}>
                <div className="text-turq text-xs font-semibold">{x.page}-bet</div>
                <div className="text-[#cfe0e6] line-clamp-2">{x.before.slice(-50)}<mark>{x.highlight}</mark>{x.after.slice(0, 50)}</div>
              </motion.li>
            ))}
          </ul>
        </motion.aside>

        <motion.section initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center gap-5">
          <PdfViewer url={api.pdfUrl(bookId)} page={page} boxes={boxes} pageWidth={cur?.page_width || 0} onLoad={setNumPages} />
          <div className="flex items-center gap-4">
            {matches.length > 0 ? (
              <>
                <Button onClick={() => go(idx - 1)} disabled={idx <= 0} className="glass" sx={{ textTransform: "none", color: "#eef6f8", borderRadius: "99px", px: 3 }}>← oldingi</Button>
                <span className="text-gold font-bold text-lg">{idx + 1} / {matches.length}</span>
                <Button onClick={() => go(idx + 1)} disabled={idx >= matches.length - 1} variant="contained" sx={{ textTransform: "none", borderRadius: "99px", px: 3, background: "linear-gradient(90deg,#1fb5c0,#2e7fd6)", color: "#fff" }}>keyingi →</Button>
              </>
            ) : (
              <>
                <Button onClick={() => setPage((p) => Math.max(1, p - 1))} className="glass" sx={{ textTransform: "none", color: "#eef6f8", borderRadius: "99px" }}>← oldingi bet</Button>
                <span className="text-gold font-bold">{page} / {numPages || "…"}</span>
                <Button onClick={() => setPage((p) => (numPages ? Math.min(numPages, p + 1) : p + 1))} className="glass" sx={{ textTransform: "none", color: "#eef6f8", borderRadius: "99px" }}>keyingi bet →</Button>
              </>
            )}
          </div>
          {cur && <p className="text-xs text-[#9fb6c1]">{page}-bet · {cur.match_type === "exact" ? "aniq moslik" : "so‘z shakli"}</p>}
        </motion.section>
      </div>
    </div>
  );
}

export default function Page() {
  return <Suspense fallback={null}><BookView /></Suspense>;
}
