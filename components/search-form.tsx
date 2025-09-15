"use client";

import { useState, useTransition } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type Props = {
  onSearch: (productUrl: string) => Promise<void> | void;
  isSearching?: boolean;
};

export function SearchForm({ onSearch, isSearching }: Props) {
  const [url, setUrl] = useState("");
  const [pending, startTransition] = useTransition();

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;
    startTransition(() => onSearch(url.trim()));
  };

  return (
    <form onSubmit={submit} className="flex gap-2 w-full max-w-3xl">
      <Input
        type="url"
        placeholder="Paste a product link from Site A…"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        className="flex-1"
        required
      />
      <Button type="submit" disabled={pending || isSearching}>
        {pending || isSearching ? "Searching…" : "Search"}
      </Button>
    </form>
  );
}