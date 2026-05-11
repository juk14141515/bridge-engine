import { useEffect, useState } from "react";
import {
  entryMemoryService,
  subscribeToEntryMemory,
  type NewEntryMemoryItem,
} from "../lib/entryMemoryService";

export function useEntryMemory() {
  const [entries, setEntries] = useState(() => entryMemoryService.list());

  useEffect(() => {
    void entryMemoryService.syncFromBackend().then(setEntries);

    return subscribeToEntryMemory(() => {
      setEntries(entryMemoryService.list());
    });
  }, []);

  function remember(input: NewEntryMemoryItem) {
    const nextEntries = entryMemoryService.add(input);
    setEntries(nextEntries);
    return nextEntries[0];
  }

  function clearMemory() {
    setEntries(entryMemoryService.clear());
  }

  function preferredPathways() {
    return entryMemoryService.preferredPathways(entries);
  }

  return { entries, remember, clearMemory, preferredPathways };
}

