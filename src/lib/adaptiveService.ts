import { createAdaptiveHelp, type AdaptiveHelpInput, type AdaptiveHelpResult } from "./adaptiveHelp";
import { apiClient } from "./apiClient";
import { createBridgePlan } from "./bridgeMapping";
import type { BridgePlan, Profile } from "../types/bridge";
import { feedbackService } from "./feedbackService";

export const adaptiveService = {
  async bridgePlan(input: {
    stuckText: string;
    chosenInterests: string[];
    profile: Profile;
    supportPreferences?: unknown;
    entryMemory?: unknown[];
  }): Promise<BridgePlan> {
    try {
      const data = await apiClient.bridgePlan({
        stuckText: input.stuckText,
        pathway: input.chosenInterests[0],
        chosenInterests: input.chosenInterests,
        supportPreferences: input.supportPreferences,
        entryMemory: input.entryMemory,
        feedback: feedbackService.list(),
      });
      return data.plan as BridgePlan;
    } catch {
      return createBridgePlan(input);
    }
  },

  async adaptiveHelp(input: AdaptiveHelpInput): Promise<AdaptiveHelpResult> {
    try {
      const data = await apiClient.adaptiveHelp({ ...input, feedback: feedbackService.list() } as AdaptiveHelpInput);
      return data.help;
    } catch {
      return createAdaptiveHelp(input);
    }
  },
};

