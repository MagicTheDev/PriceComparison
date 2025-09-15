export type AutoItem = {
  id: string;
  title: string;
  image?: string | null;
  url?: string | null;
};
export type AutoResponse = { items: AutoItem[] };