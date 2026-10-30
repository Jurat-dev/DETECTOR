"use client";
import { Suspense, useEffect, useState } from "react";
import { AnimatePresence, LayoutGroup, motion } from "framer-motion";
import { useRouter, useSearchParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Radar from "@/components/Radar";
import Logo from "@/components/Logo";
import SearchBar from "@/components/SearchBar";
import ResultCard from "@/components/ResultCard";
import { api, type BookResult } from "@/lib/api";

function Home() {
  const router = useRouter();
  const params = useSearchParams();
  const q = params.get("q") || "";
  const [intro, setIntro] = useState(true);
  const [opening, setOpening] = useState<BookResult | null>(null);

  useEffect(() => {
    if (sessionStorage.getItem("detector-intro") || q) { setIntro(false); return; }
    const t = setTimeout(() => { setIntro(false); sessionStorage.setItem("detector-intro", "1"); }, 2600);
    return () => clearTimeout(t);
  }, [q]);

  const { data, isFetching, error } = useQuery({ queryKey: ["search", q], queryFn: () => api.search(q), enabled: !!q });

  const onSearch = (s: string) => router.push(`/?q=${encodeURIComponent(s)}`);
  const open = (r: BookResult, page?: number) => {
    setOpening(r);
    setTimeout(() => router.push(`/book/${r.book.id}?q=${encodeURIComponent(q)}${page ? `&page=${page}` : ""}`), 420);
  };

  return (
    <LayoutGroup>
      <AnimatePresence>
        {intro && (
          <motion.div key="intro" className="fixed inset-0 z-50 flex flex-col items-center justify-center gap-8" exit={{ opacity: 1 }}>
            <motion.div layoutId="detector-radar" transition={{ type: "spring", stiffness: 70, damping: 16 }}>
              <Radar size={300} speed={2} />
            </motion.div>
            <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="text-[#9fb6c1] tracking-[0.3em] uppercase text-sm">Kitoblar skanerlanmoqda…</motion.p>
          </motion.div>
        )}
      </AnimatePresence>

      <header className="flex justify-between items-center px-6 md:px-12 py-6">
        {!intro ? <Logo scanning={isFetching} /> : <div className="h-10" />}
        <nav className="hidden md:flex gap-7 text-sm text-[#b9cdd6]"><span>Qidiruv</span><span>Kitoblar</span><span>Yordam</span></nav>
      </header>

      <motion.main initial={{ opacity: 0 }} animate={{ opacity: intro ? 0 : 1 }} transition={{ delay: intro ? 0 : 0.3 }} className="max-w-6xl mx-auto px-6 pb-32">
        <motion.section layout className={q ? "pt-2" : "pt-[12vh] text-center"}>
          {!q && (
            <>
              <h1 className="text-4xl md:text-6xl font-extrabold mb-4">Kitoblardan <span className="brand">aniq</span> toping</h1>
              <p className="text-[#b9cdd6] mb-10 text-lg">So‘z yoki ibora qaysi kitobda, qaysi betda borligini ko‘rsatamiz.</p>
            </>
          )}
          <div className="max-w-3xl mx-auto"><SearchBar initial={q} onSearch={onSearch} loading={isFetching} /></div>
        </motion.section>

        <AnimatePresence mode="wait">
          {isFetching && (
            <motion.div key="scan" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center gap-4 py-16">
              <Radar size={160} speed={1.2} />
              <p className="text-turq">«{q}» skanerlanmoqda…</p>
            </motion.div>
          )}
        </AnimatePresence>

        {error && <p className="text-center text-red-300 py-10">Serverga ulanib bo‘lmadi. Backend ishlayotganini tekshiring.</p>}

        {data && !isFetching && (
          <div className="mt-8">
            <p className="text-[#b9cdd6] mb-5">
              «<span className="text-gold font-semibold">{data.query}</span>» — {data.books.length} ta kitobda {data.total} ta moslik
            </p>
            <motion.div className="grid md:grid-cols-2 gap-5" initial="hidden" animate="show" variants={{ show: { transition: { staggerChildren: 0.09 } } }}>
              {data.books.map((r) => <ResultCard key={r.book.id} r={r} onOpen={open} />)}
            </motion.div>
            {data.books.length === 0 && (
              <div className="glass p-6 mt-2">
                <p className="mb-4">Aniq moslik topilmadi.</p>
                {data.approximate.length > 0 && (
                  <>
                    <p className="text-sm text-gold mb-3">Ma’no bo‘yicha taxminiy natijalar:</p>
                    <ul className="flex flex-col gap-3">
                      {data.approximate.map((a, i) => (
                        <li key={i} className="bg-white/5 hover:bg-white/10 rounded-lg p-3 cursor-pointer text-sm" onClick={() => router.push(`/book/${a.book.id}?page=${a.page}`)}>
                          <span className="tag tag-gold mr-2">taxminiy</span><b>{a.book.title}</b> · {a.page}-bet
                          <p className="text-[#cfe0e6] mt-1">{a.text}</p>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </motion.main>

      <AnimatePresence>
        {opening && (
          <motion.div layoutId={`card-${opening.book.id}`} className="glass fixed inset-4 z-40 flex items-center justify-center" transition={{ type: "spring", stiffness: 90, damping: 18 }}>
            <div className="text-center"><Radar size={90} speed={1} /><p className="mt-4 font-bold">{opening.book.title}</p></div>
          </motion.div>
        )}
      </AnimatePresence>
    </LayoutGroup>
  );
}

export default function Page() {
  return <Suspense fallback={null}><Home /></Suspense>;
}
