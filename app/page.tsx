"use client";

import { useState } from "react";
import ProductCard from "../components/product-card";
import PossibleMatches from "../components/possible-matches";
import { AutocompleteInput } from "../components/autocomplete-input";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import type {
  Product,
  LesliesSearchResponse,
  LesliesSearchItem,
} from "../types/product";
import type { AutoItem } from "@/types/autocomplete";


export default function HomePage() {
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);

  const [pool360, setPool360] = useState<Product | null>(null);
  const [lesliesResults, setLesliesResults] = useState<LesliesSearchItem[]>([]);
  const [compare, setCompare] = useState<Product[]>([]);
  const [addingPid, setAddingPid] = useState<string | null>(null);

  const [selectedAuto, setSelectedAuto] = useState<AutoItem | null>(null);

  async function handleSearch(e: React.FormEvent) {
  e.preventDefault();
  const text = q.trim();
  if (!text && !selectedAuto) return;

  setLoading(true);
  setCompare([]);
  try {
    // 👉 Prefer ID if an autocomplete item was chosen
    const poolKey = selectedAuto?.id ?? text;

    // Pool360 (by id or by name, same endpoint if your backend supports both)
    const p360Res = await fetch(`/api/product/pool360?product_name=${encodeURIComponent(poolKey)}`, {
      cache: "no-store",
    });
    if (!p360Res.ok) throw new Error("Pool360 fetch failed");
    const p360 = (await p360Res.json()) as Product;
    setPool360(p360);

    // Leslie's candidates — still search by text (use picked title if available)
    const lesQuery = selectedAuto?.title ?? text;
    const lRes = await fetch(`/api/search/leslies?product_name=${encodeURIComponent(lesQuery)}`, {
      cache: "no-store",
    });
    if (!lRes.ok) throw new Error("Leslie's search failed");
    const { items } = (await lRes.json()) as { items: LesliesSearchItem[] };
    setLesliesResults(items ?? []);
  } catch (err: any) {
    toast.error(err?.message ?? "Search failed");
    setPool360(null);
    setLesliesResults([]);
  } finally {
    setLoading(false);
  }
}

  async function addLeslies(item: LesliesSearchItem) {
    try {
      setAddingPid(item.pid);

      const res = await fetch(`/api/product/leslies/${encodeURIComponent(item.pid)}`, {
        cache: "no-store",
      });
      if (!res.ok) throw new Error("Could not fetch Leslie's product");

      const full = (await res.json()) as Product;

      setCompare(prev =>
        prev.find(p => p.id === full.id) ? prev : [...prev, full]
      );

      // ✅ remove from suggestions
      setLesliesResults(prev => prev.filter(x => x.pid !== item.pid));
    } catch (e: any) {
      toast.error(e?.message ?? "Failed to add");
    } finally {
      setAddingPid(null);
    }
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 space-y-8">
      <h1 className="text-3xl font-bold tracking-tight">Product Finder</h1>
      <form onSubmit={handleSearch} className="flex gap-2 max-w-3xl">
        <AutocompleteInput
          value={q}
          onChange={(v) => {
            setQ(v);
            setSelectedAuto(null); // typing cancels a previous pick
          }}
          onSelect={(item) => {
            setQ(item.title ?? "");   // show title in the box
            setSelectedAuto(item);    // remember the chosen item (has id)
          }}
        />
        <Button type="submit" disabled={loading}>
          {loading ? "Searching…" : "Search"}
        </Button>
      </form>

      {/* Comparison row */}
      {pool360 && (
        <section>
        <h2 className="text-xl font-semibold mb-3">Compare</h2>
        <div className="grid gap-6 grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {pool360 && <ProductCard p={pool360} />}
          {compare.map((p) => (
            <ProductCard key={p.id} p={p} />
          ))}
        </div>
      </section>
      )}

      {/* Leslie's candidates */}
      <section>
        {lesliesResults.length ? (
          <PossibleMatches items={lesliesResults} onAdd={addLeslies} addingPid={addingPid} />
        ) : (
          <p className="text-muted-foreground">No candidates yet. Try a search.</p>
        )}
      </section>
    </main>
  );
}