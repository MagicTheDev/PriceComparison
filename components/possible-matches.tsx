"use client";

import { useRef } from "react";
import Image from "next/image";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { LesliesSearchItem } from "@/types/product";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export default function PossibleMatches({
  items,
  onAdd,
  addingPid,
}: {
  items: LesliesSearchItem[];
  onAdd: (item: LesliesSearchItem) => void;
  addingPid?: string | null;
}) {
  const scrollRef = useRef<HTMLDivElement>(null);
  if (!items?.length) return null;

  const scroll = (dir: "left" | "right") => {
    const el = scrollRef.current;
    if (!el) return;
    const amount = 320; // px per click
    el.scrollBy({ left: dir === "left" ? -amount : amount, behavior: "smooth" });
  };

  return (
    <div className="flex flex-col gap-3">

        {/* Arrows row */}
        <div className="flex justify-between mb-3">
        <h2 className="text-xl font-semibold mb-3">Possible matches (Leslie)</h2>
        <div className="flex gap-2">
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={() => scroll("left")}
          className="rounded-full"
          aria-label="Scroll left"
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={() => scroll("right")}
          className="rounded-full"
          aria-label="Scroll right"
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
        </div>
            </div>

        {/* Scroll area */}
        <div ref={scrollRef} className="overflow-x-auto">
        <div className="flex gap-4 pb-2">
          {items.map((it) => {
            const price = it.sale_price ?? it.price;
            return (
              <Card
                key={it.pid}
                className="min-w-[280px] max-w-[280px] shrink-0 overflow-hidden"
              >
                <div className="grid grid-rows-[auto,1fr,auto] gap-3 p-3 h-full">
                  <div className="relative w-full h-[150px] bg-muted">
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
                      <CardTitle className="text-base line-clamp-2">
                        {it.title}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0 mt-1">
                      <div className="flex items-center gap-2 mb-1">
                        {it.brand && <Badge variant="outline">{it.brand}</Badge>}
                      </div>
                      {price != null && (
                        <div className="text-lg font-semibold">
                          ${Number(price).toFixed(2)}
                        </div>
                      )}
                      <a
                        href={it.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-xs text-primary hover:underline"
                      >
                        Product page →
                      </a>
                    </CardContent>
                  </div>

                  <div className="mt-auto">
                    <Button
                      size="sm"
                      onClick={() => onAdd(it)}
                      disabled={addingPid === it.pid}
                      className="w-full"
                    >
                      {addingPid === it.pid ? "Adding…" : "+ Add"}
                    </Button>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
        </div>


    </div>
  );
}