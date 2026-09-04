create table if not exists orders (
  id          uuid primary key,
  item        text        not null,
  quantity    int         not null,
  enriched    boolean     not null,
  created_at  timestamptz not null default now()
);
