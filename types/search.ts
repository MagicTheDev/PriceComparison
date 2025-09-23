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

export type Stock = {
  location: string;
  qty: number;
};

export type Product = {
  id: string;
  name: string;
  description?: string;
  product_number?: string;
  url: string;
  price: string;              // as returned (could be string/number)
  unit_of_measure?: string;
  stock: Stock[];
  site?: string;
  images: string[];
  brand_name?: string;
};