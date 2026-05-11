import { nanoId } from "./ids";
import { apiClient } from "./apiClient";
import type { BridgeFeedbackItem } from "../types/bridge";

const STORAGE_KEY = "bridge.feedback.v1";

export const feedbackService = {
  async save(input: Omit<BridgeFeedbackItem, "id">) {
    const localItem: BridgeFeedbackItem = { ...input, id: nanoId("feedback") };
    writeFeedback([localItem, ...readFeedback()].slice(0, 120));

    if (apiClient.hasSession()) {
      try {
        return await apiClient.bridgeFeedback(input);
      } catch {
        return { feedback: localItem };
      }
    }

    return { feedback: localItem };
  },

  list() {
    return readFeedback();
  },
};

function readFeedback(): BridgeFeedbackItem[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as BridgeFeedbackItem[]) : [];
  } catch {
    return [];
  }
}

function writeFeedback(items: BridgeFeedbackItem[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

