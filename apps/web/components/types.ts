export type SearchResult = {
  id: string;
  platform: string;
  title: string | null;
  snippet: string;
  author: string | null;
  url: string;
  created_at: string | null;
  score: number;
};

export type SearchResponse = {
  query: string;
  total: number;
  results: SearchResult[];
};
