import { nanoId } from "./ids";
import type { EntryMemoryItem } from "../types/bridge";
import { apiClient } from "./apiClient";

const STORAGE_KEY = "bridge.entryMemory.v1";
const CHANGE_EVENT = "bridge-entry-memory-change";

export type NewEntryMemoryItem = Omit<EntryMemoryItem, "id" | "createdAt">;

export const entryMemoryService = {
  list(): EntryMemoryItem[] {
    return readEntries();
  },

  async syncFromBackend(): Promise<EntryMemoryItem[]> {
    if (!apiClient.hasSession()) return readEntries();

    try {
      const data = await apiClient.getEntryMemory();
      writeEntries(data.entries);
      notifyChange();
      return data.entries;
    } catch {
      return readEntries();
    }
  },

  add(input: NewEntryMemoryItem): EntryMemoryItem[] {
    const next: EntryMemoryItem = { ...input, id: nanoId("entry"), createdAt: Date.now() };
    const entries = [next, ...readEntries()].slice(0, 80);
    writeEntries(entries);
    notifyChange();

    if (apiClient.hasSession()) {
      void apiClient
        .bridgeOutcome(input)
        .then((data) => {
          writeEntries(data.entries);
          notifyChange();
        })
        .catch(() => undefined);
    }

    return entries;
  },

  clear(): EntryMemoryItem[] {
    writeEntries([]);
    notifyChange();
    return [];
  },

  preferredPathways(entries = readEntries()): string[] {
    const counts = new Map<string, number>();
    for (const item of entries) {
      counts.set(item.attentionPathway, (counts.get(item.attentionPathway) ?? 0) + 1);
    }
    return [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([pathway]) => pathway);
  },
};

export function subscribeToEntryMemory(listener: () => void) {
  window.addEventListener(CHANGE_EVENT, listener);
  return () => window.removeEventListener(CHANGE_EVENT, listener);
}

function readEntries(): EntryMemoryItem[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as EntryMemoryItem[]) : [];
  } catch {
    return [];
  }
}

function writeEntries(entries: EntryMemoryItem[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

function notifyChange() {
  window.dispatchEvent(new Event(CHANGE_EVENT));
}

