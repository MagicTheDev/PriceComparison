// /app/page.tsx
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import ProductCard from "@/components/product-card";
import { SiteSection } from "@/components/site-section";
import type { Product } from "@/types/search";
import type { SearchResponse, SiteBucket, SearchItem } from "@/types/search";
import { toast } from "sonner";

export default function Home() {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<SearchResponse | null>(null);

  // persistent compare list across searches
  const [compare, setCompare] = useState<Product[]>([]);
  const [addingPid, setAddingPid] = useState<string | null>(null);

  async function runSearch() {
    const query = q.trim();
    if (!query) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/search/items?query=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error("Search failed");
      const data = (await res.json()) as SearchResponse;
      setResults(data ?? {});
    } catch (e) {
      console.error(e);
      toast.error("Search failed");
      setResults(null);
    } finally {
      setLoading(false);
    }
  }

  async function addToCompare(siteKey: string, item: SearchItem) {
    if (compare.some((c) => c.id === item.pid)) {
      toast.info("Already in compare");
      return;
    }
    setAddingPid(item.pid);
    try {
      const url = `/api/product?site=${encodeURIComponent(siteKey)}&product_id=${encodeURIComponent(item.pid)}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error("Load product failed");
      const full = (await res.json()) as Product;
      setCompare((prev) => [...prev, full]);

      // remove from suggestions after adding
      setResults((prev) => {
        if (!prev) return prev;
        const copy: SearchResponse = { ...prev };
        const bucket = copy[siteKey];
        if (bucket) {
          copy[siteKey] = { ...bucket, items: bucket.items.filter((x) => x.pid !== item.pid) };
        }
        return copy;
      });
    } catch (e) {
      console.error(e);
      toast.error("Could not add product");
    } finally {
      setAddingPid(null);
    }
  }

  function clearCompare() {
    setCompare([]);
  }

  return (
    <main className="container mx-auto max-w-6xl py-8">
      {/* Search bar */}
      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();
          runSearch();
        }}
      >
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search product name…"
        />
        <Button type="submit" disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </Button>
      </form>

      {/* Compare row (persists across searches) */}
      {compare.length > 0 && (
        <section className="mt-8">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-xl font-semibold">Compare</h2>
            <Button variant="outline" size="sm" onClick={clearCompare}>
              Clear
            </Button>
          </div>
          <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {compare.map((p) => (
              <ProductCard key={p.id} p={p} />
            ))}
          </div>
        </section>
      )}

      {/* Site sections */}
      {results && (
        <>
          {Object.entries(results).map(([siteKey, bucket]) => {
            const b = bucket as SiteBucket;
            return (
              <SiteSection
                key={siteKey}
                siteKey={siteKey}
                siteLabel={b.site || siteKey}
                items={b.items || []}
                onAdd={addToCompare}
                addingPid={addingPid}
              />
            );
          })}
        </>
      )}

      {!loading && results && Object.values(results).every((b) => !b.items?.length) && (
        <p className="mt-8 text-sm text-muted-foreground">No results.</p>
      )}
    </main>
  );
}
``