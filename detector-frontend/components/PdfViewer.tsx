"use client";
import { Document, Page, pdfjs } from "react-pdf";
import { Component, type ReactNode, useEffect, useRef, useState } from "react";
import type { BBox } from "@/lib/api";

pdfjs.GlobalWorkerOptions.workerSrc = new URL("pdfjs-dist/build/pdf.worker.min.mjs", import.meta.url).toString();

// PDF.js xatosi (masalan 404) butun sahifani yiqitmasligi uchun
class PdfBoundary extends Component<{ children: ReactNode }, { err: boolean }> {
  state = { err: false };
  static getDerivedStateFromError() { return { err: true }; }
  componentDidCatch(e: unknown) { console.error("PDF ko'rsatishda xato:", e); }
  render() { return this.state.err ? <div className="text-red-300 p-10">PDF ochilmadi.</div> : this.props.children; }
}

export default function PdfViewer(props: { url: string; page: number; boxes: BBox[]; pageWidth: number; onLoad?: (n: number) => void }) {
  // Avval PDF mavjudligini tekshiramiz: 404 bo'lsa PDF.js ga umuman bermaymiz
  const [status, setStatus] = useState<"checking" | "ok" | "missing">("checking");
  useEffect(() => {
    const ac = new AbortController();
    setStatus("checking");
    fetch(props.url, { headers: { Range: "bytes=0-1023" }, signal: ac.signal })
      .then((r) => { setStatus(r.ok ? "ok" : "missing"); ac.abort(); })
      .catch((e) => { if (e?.name !== "AbortError") setStatus("missing"); });
    return () => ac.abort();
  }, [props.url]);
  if (status === "checking") return <div className="text-[#9fb6c1] p-10">PDF yuklanmoqda…</div>;
  if (status === "missing") return <div className="text-red-300 p-10">PDF fayl serverda topilmadi. Matndagi mosliklar chap tomonda ko‘rsatilgan.</div>;
  return <PdfBoundary><PdfInner {...props} /></PdfBoundary>;
}

function PdfInner({ url, page, boxes, pageWidth, onLoad }: { url: string; page: number; boxes: BBox[]; pageWidth: number; onLoad?: (n: number) => void }) {
  const wrap = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(600);
  const [rendered, setRendered] = useState({ w: 0, origW: 0 });
  useEffect(() => {
    const el = wrap.current; if (!el) return;
    const ro = new ResizeObserver(() => setWidth(Math.min(760, el.clientWidth)));
    ro.observe(el); return () => ro.disconnect();
  }, []);
  const firstBox = useRef<HTMLDivElement>(null);
  // topilgan so'zni ko'rinadigan joyga olib kelish
  useEffect(() => {
    if (!rendered.origW || !boxes.length) return;
    const t = setTimeout(() => firstBox.current?.scrollIntoView({ behavior: "smooth", block: "center" }), 80);
    return () => clearTimeout(t);
  }, [rendered, page, boxes.length, boxes[0]?.y0]); // eslint-disable-line react-hooks/exhaustive-deps
  const scale = rendered.origW ? width / rendered.origW : pageWidth ? width / pageWidth : 1;
  return (
    <div ref={wrap} className="w-full flex justify-center">
      <Document file={url} onLoadError={(e) => console.error("PDF yuklanmadi:", e)} onSourceError={(e) => console.error("PDF manbasi xato:", e)} onLoadSuccess={(d) => onLoad?.(d.numPages)}
        loading={<div className="text-[#9fb6c1] p-10">PDF yuklanmoqda…</div>}
        error={<div className="text-red-300 p-10">PDF ochilmadi.</div>}>
        <div className="relative rounded-md overflow-hidden shadow-2xl">
          <Page pageNumber={page} width={width} renderTextLayer={false} renderAnnotationLayer={false}
            onLoadSuccess={(p) => setRendered({ w: width, origW: p.originalWidth })} />
          {boxes.map((b, i) => (
            <div key={`${page}-${i}`} ref={i === 0 ? firstBox : undefined} className="pdf-glow" style={{ left: b.x0 * scale - 2, top: b.y0 * scale - 2, width: (b.x1 - b.x0) * scale + 4, height: (b.y1 - b.y0) * scale + 4 }} />
          ))}
        </div>
      </Document>
    </div>
  );
}
