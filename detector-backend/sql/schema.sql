-- Detector: Supabase Postgres sxemasi
create extension if not exists pg_trgm;
create extension if not exists vector;
create extension if not exists unaccent;

create table if not exists books (
  id serial primary key,
  title text not null,
  author text,
  file_url text not null,
  page_count int not null default 0,
  source_type text not null default 'text' check (source_type in ('text','ocr','mixed'))
);

create table if not exists pages (
  id bigserial primary key,
  book_id int not null references books(id) on delete cascade,
  page_number int not null,
  text_raw text not null default '',
  text_norm text not null default '',
  source text not null default 'text' check (source in ('text','ocr')),
  ocr_confidence real,
  tsv tsvector generated always as (to_tsvector('simple', text_norm)) stored,
  unique (book_id, page_number)
);
create index if not exists pages_tsv_idx on pages using gin (tsv);
create index if not exists pages_trgm_idx on pages using gin (text_norm gin_trgm_ops);

create table if not exists chunks (
  id bigserial primary key,
  book_id int not null references books(id) on delete cascade,
  page_number int not null,
  text text not null,
  text_norm text not null default '',
  embedding vector(1024)
);
create index if not exists chunks_book_idx on chunks (book_id, page_number);
create index if not exists chunks_emb_idx on chunks using hnsw (embedding vector_cosine_ops);

create table if not exists words (
  id bigserial primary key,
  page_id bigint not null references pages(id) on delete cascade,
  word text not null,
  word_norm text not null,
  x0 real not null, y0 real not null, x1 real not null, y1 real not null,
  page_width real, page_height real
);
create index if not exists words_page_idx on words (page_id);
create index if not exists words_norm_idx on words (word_norm);
create index if not exists words_trgm_idx on words using gin (word_norm gin_trgm_ops);

-- Semantik qidiruv funksiyasi
create or replace function match_chunks(query_embedding vector(1024), match_count int default 10)
returns table (id bigint, book_id int, page_number int, text text, similarity float)
language sql stable as $$
  select c.id, c.book_id, c.page_number, c.text, 1 - (c.embedding <=> query_embedding) as similarity
  from chunks c where c.embedding is not null
  order by c.embedding <=> query_embedding limit match_count;
$$;
