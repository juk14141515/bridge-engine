import { useEffect, useMemo, useState } from "react";

function safeParse<T>(raw: string | null): T | null {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

export function useLocalStorageState<T>(key: string, initial: T) {
  const [state, setState] = useState<T>(() => {
    const parsed = safeParse<T>(localStorage.getItem(key));
    return parsed ?? initial;
  });

  const api = useMemo(() => ({ state, setState }), [state]);

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(state));
  }, [key, state]);

  return api;
}

