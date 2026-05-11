import type { Profile } from "../types/bridge";
import { useLocalStorageState } from "./useLocalStorageState";

const defaultProfile: Profile = {
  displayName: "",
  interests: ["gaming", "coding", "systems", "fitness"],
  motivationDrivers: ["curiosity", "identity", "future self"],
  proofPreference: "one_sentence",
  pacingPreference: "tiny",
  stimulationPreference: "low",
  coachTone: "calm",
};

export function useProfile() {
  return useLocalStorageState<Profile>("bridge.profile.v1", defaultProfile);
}

