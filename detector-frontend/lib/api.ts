export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

export type Book = { id: number; title: string; author: string; page_count: number; source_type: string };
export type Snippet = { page: number; match_type: "exact" | "forms"; text: string; before: string; highlight: string; after: string };
export type BookResult = { book: Book; count: number; exact_count: number; forms_count: number; pages: number; match_type: "exact" | "forms"; snippets: Snippet[] };
export type Approx = { book: Book; page: number; score: number; text: string; approximate: true };
export type SearchResponse = { query: string; total: number; books: BookResult[]; approximate: Approx[] };
export type BBox = { x0: number; y0: number; x1: number; y1: number };
export type Match = Snippet & { index: number; bbox: BBox[]; page_width: number; page_height: number };
export type MatchesResponse = { book: Book; query: string; total: number; matches: Match[] };
export type Source = { n: number; book_id: number; title: string; page: number; text: string; approximate?: boolean };
export type ChatResponse = { answer: string; found: boolean; sources: Source[] };

async function get<T>(path: string): Promise<T> {
  const r = await fetch(API_URL + path);
  if (!r.ok) throw new Error(`Server xatosi: ${r.status}`);
  return r.json();
}

export const api = {
  search: (q: string) => get<SearchResponse>(`/search?q=${encodeURIComponent(q)}`),
  book: (id: number) => get<Book>(`/books/${id}`),
  matches: (id: number, q: string) => get<MatchesResponse>(`/books/${id}/matches?q=${encodeURIComponent(q)}`),
  pdfUrl: (id: number) => `${API_URL}/books/${id}/pdf`,
  chat: async (question: string): Promise<ChatResponse> => {
    const r = await fetch(API_URL + "/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }) });
    if (!r.ok) throw new Error(`Server xatosi: ${r.status}`);
    return r.json();
  },
};
