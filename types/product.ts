// Pool360
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

// Leslie's (search result)
export type LesliesSearchItem = {
  pid: string;
  title: string;
  url: string;
  price?: number;
  sale_price?: number;
  brand?: string;
  description?: string;   // may be HTML
  thumb_image?: string;
};

export type LesliesSearchResponse = {
  items: LesliesSearchItem[];
};
