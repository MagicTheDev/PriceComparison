"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import Image from "next/image";
import { cn } from "@/lib/utils"; // if you have it; otherwise remove cn()
import type { AutoItem, AutoResponse } from "@/types/autocomplete";
import { Input } from "@/components/ui/input";

type Props = {
  value: string;
  onChange: (v: string) => void;
  onSelect: (item: AutoItem) => void; // what to do when user picks a suggestion
  placeholder?: string;
  minChars?: number;
};

export function AutocompleteInput({
  value,
  onChange,
  onSelect,
  placeholder = "Search product name…",
  minChars = 2,
}: Props) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState<AutoItem[]>([]);
  const wrapRef = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState<number | null>(null);

  // Close when clicking outside
  useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      if (!wrapRef.current?.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", onDocClick);
    return () => document.removeEventListener("mousedown", onDocClick);
  }, []);

  // Debounced fetch
  useEffect(() => {
    if (value.trim().length < minChars) {
      setItems([]);
      setOpen(false);
      return;
    }
    const ac = new AbortController();
    setLoading(true);

    const t = setTimeout(async () => {
      try {
        // accept either /autocomplete or the misspelled /autoccomplete
        const enc = encodeURIComponent(value.trim());
        const res = await fetch(`/api/autocomplete?query=${enc}`, { signal: ac.signal })
          .catch(() => fetch(`/api/autoccomplete?query=${enc}`, { signal: ac.signal }));
        if (!res || !res.ok) throw new Error("autocomplete fetch failed");
        const data = (await res.json()) as AutoResponse;
        const list = (data?.items ?? []).slice(0, 10);
        setItems(list);
        setActive(null);
        setOpen(list.length > 0);
      } catch (_) {
        if (!ac.signal.aborted) { setItems([]); setOpen(false); }
      } finally {
        if (!ac.signal.aborted) setLoading(false);
      }
    }, 200); // debounce 200ms

    return () => { ac.abort(); clearTimeout(t); };
  }, [value, minChars]);

  // keyboard navigation
  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!open || items.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((prev) => {
        if (prev === null) return 0;        // start at first
        return (prev + 1) % items.length;   // cycle down
      });
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((prev) => {
        if (prev === null) return items.length - 1; // start at last
        return (prev - 1 + items.length) % items.length;
      });
    } else if (e.key === "Enter") {
      if (active !== null) {
        e.preventDefault();
        const item = items[active];
        if (item) {
          onSelect(item);
          setOpen(false);
        }
      }
      // else: let the form submit with the plain input value
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  }

  return (
    <div ref={wrapRef} className="relative w-full">
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => items.length && setOpen(true)}
        onKeyDown={onKeyDown}
        placeholder={placeholder}
        aria-autocomplete="list"
        aria-expanded={open}
        aria-controls="autocomplete-list"
      />
      {open && (
        <div
          id="autocomplete-list"
          role="listbox"
          className="absolute z-20 mt-1 w-full overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md"
        >
          <ul className="max-h-80 overflow-auto py-1">
            {items.map((it, i) => (
              <li
                key={it.id}
                onMouseEnter={() => setActive(i)}
                className={`flex items-center gap-3 px-3 py-2 cursor-pointer
                  ${active === i ? "bg-accent text-accent-foreground" : ""}`}
              >
                <div className="relative h-10 w-10 shrink-0 rounded bg-muted">
                  {it.image && (
                    <Image
                      src={it.image}
                      alt={it.title || "product"}
                      fill
                      className="object-contain"
                      unoptimized
                    />
                  )}
                </div>
                <span className="line-clamp-2 text-sm">{it.title}</span>
              </li>
            ))}
            {!items.length && !loading && (
              <li className="px-3 py-2 text-sm text-muted-foreground">No matches</li>
            )}
            {loading && (
              <li className="px-3 py-2 text-sm text-muted-foreground">Searching…</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}