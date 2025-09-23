// /types/search.ts
export type SearchItem = {
  pid: string;
  title: string;
  url: string;
  price?: string | number | null;
  brand?: string | null;
  description?: string | null;
  thumb_image?: string | null;
};

export type SiteBucket = {
  site: string;          // e.g. "Pool360"
  items: SearchItem[];
};

// API returns an object keyed by site, each value is a SiteBucket
export type SearchResponse = Record<string, SiteBucket>;

// whatever your detailed product schema already is
export type Product = {
  id: string;
  name: string;
  description?: string | null;
  product_number?: string | null;
  site: string;
  url?: string | null;
  images?: string[];
  price?: number | string | null;
  stock?: Array<{ location: string; qty: number }>;
  brand_name?: string | null;
  // …etc
};