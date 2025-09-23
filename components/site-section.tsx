// /components/site-section.tsx
"use client";
import Image from "next/image";
import { useRef } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { SearchItem } from "@/types/search";

export function SiteSection({
  siteKey,
  siteLabel,
  items,
  onAdd,
  addingPid,
}: {
  siteKey: string;
  siteLabel: string;
  items: SearchItem[];
  onAdd: (siteKey: string, item: SearchItem) => void;
  addingPid?: string | null;
}) {
  if (!items?.length) return null;

  const scRef = useRef<HTMLDivElement>(null);
  const scroll = (dir: "left" | "right") => {
    const el = scRef.current;
    if (!el) return;
    const step = Math.min(400, el.clientWidth * 0.9);
    el.scrollBy({ left: dir === "left" ? -step : step, behavior: "smooth" });
  };

  return (
    <section className="mt-8">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-xl font-semibold">{siteLabel}</h2>
        <div className="flex gap-2">
          <Button variant="outline" size="icon" onClick={() => scroll("left")} aria-label="Scroll left">
            <ChevronLeft className="h-5 w-5" />
          </Button>
          <Button variant="outline" size="icon" onClick={() => scroll("right")} aria-label="Scroll right">
            <ChevronRight className="h-5 w-5" />
          </Button>
        </div>
      </div>

      <div ref={scRef} className="overflow-x-auto [scrollbar-width:none] [-ms-overflow-style:none]">
        <div className="flex gap-4 min-w-full">
          {items.map((it) => {
            const price = typeof it.price === "string" ? it.price : it.price != null ? `$${Number(it.price).toFixed(2)}` : undefined;
            return (
              <Card key={it.pid} className="w-[320px] shrink-0 overflow-hidden">
                <div className="p-3 grid grid-cols-[120px,1fr] gap-3">
                  <div className="relative h-[90px] w-[120px] bg-muted rounded">
                    {it.thumb_image && (
                      <Image
                        src={it.thumb_image}
                        alt={it.title}
                        fill
                        className="object-contain"
                        unoptimized
                      />
                    )}
                  </div>
                  <div>
                    <CardHeader className="p-0">
                      <CardTitle className="text-base line-clamp-2">{it.title}</CardTitle>
                    </CardHeader>
                    <CardContent className="p-0 mt-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">{siteLabel}</Badge>
                        {it.brand && <Badge variant="outline">{it.brand}</Badge>}
                      </div>
                      {price && <div className="font-semibold">{price}</div>}
                      <a href={it.url} className="text-xs text-primary hover:underline" target="_blank" rel="noreferrer">
                        Product page →
                      </a>
                    </CardContent>
                  </div>
                </div>
                <div className="p-3 pt-0">
                  <Button
                    className="w-full"
                    size="sm"
                    onClick={() => onAdd(siteKey, it)}
                    disabled={addingPid === it.pid}
                  >
                    {addingPid === it.pid ? "Adding…" : "+ Add to Compare"}
                  </Button>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
}