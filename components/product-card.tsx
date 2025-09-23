import Image from "next/image";
import { Card, CardHeader, CardTitle, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Separator } from "./ui/separator";

export default function ProductCard({ p }: { p }) {
  const img = p.images?.[0];
  const price = p.price;

  return (
    <Card className="overflow-hidden">
      {img && (
        <div className="relative aspect-[4/3] w-full bg-muted">
          <Image src={img} alt={p.name} fill className="object-cover" unoptimized />
        </div>
      )}
      <CardHeader>
        <CardTitle className="line-clamp-2">{p.name}</CardTitle>
        <div className="flex gap-2 text-sm text-muted-foreground">
          {p.brand_name && <Badge variant="outline">{p.brand_name}</Badge>}
          {p.site && <Badge variant="secondary">{p.site}</Badge>}
          {p.unit_of_measure && <Badge variant="outline">{p.unit_of_measure}</Badge>}
        </div>
      </CardHeader>
      <Separator />
      <CardContent className="space-y-4 pt-4">
        <div className="flex items-baseline justify-between">
          <div className="text-2xl font-semibold">{price}</div>
          <a
            href={p.url}
            target="_blank"
            rel="noreferrer"
            className="text-sm text-primary hover:underline"
          >
            View →
          </a>
        </div>

        {/* Stock locations */}
        {p.stock?.length ? (
          <div>
            <div className="text-sm font-medium mb-2">Stock:</div>
            <ul className="text-sm grid gap-1">
              {p.stock.slice(0, 5).map((s, i) => (
                <li key={i} className="flex justify-between">
                  <span className="text-muted-foreground">{s.location}</span>
                  <span className="font-medium">{s.qty}</span>
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {p.description && (
          <p className="text-sm text-muted-foreground line-clamp-4">{p.description}</p>
        )}
      </CardContent>
    </Card>
  );
}