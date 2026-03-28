import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { getPaginated } from "../client";

export type SearchEntityType = "deal" | "prospect" | "account" | "contact" | "note";

export interface GlobalSearchHit {
  id: string;
  type: SearchEntityType;
  title: string;
  subtitle: string | null;
  href: string;
  score: number;
}

const DEFAULT_DEBOUNCE_MS = 320;

export function useGlobalSearch(
  query: string,
  entityTypes?: SearchEntityType[],
  debounceMs: number = DEFAULT_DEBOUNCE_MS,
) {
  const [debouncedQuery, setDebouncedQuery] = useState(query);

  useEffect(() => {
    const id = window.setTimeout(() => setDebouncedQuery(query), debounceMs);
    return () => window.clearTimeout(id);
  }, [query, debounceMs]);

  const trimmed = debouncedQuery.trim();
  const enabled = trimmed.length >= 2;

  return useQuery({
    queryKey: ["search", "global", trimmed, entityTypes ?? null],
    queryFn: () =>
      getPaginated<GlobalSearchHit>("/v1/search", {
        params: {
          q: trimmed,
          types: entityTypes?.length ? entityTypes.join(",") : undefined,
          page: 1,
          page_size: 25,
        },
      }),
    enabled,
    staleTime: 30 * 1000,
  });
}
