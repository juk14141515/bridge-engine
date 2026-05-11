import { useEffect } from "react";
import type { AccessibilityPrefs } from "../types/bridge";
import { useLocalStorageState } from "./useLocalStorageState";

const defaults: AccessibilityPrefs = {
  reducedMotion: false,
  highReadability: false,
  lowStimulation: false,
  colorblindSafe: true,
};

export function useAccessibilityPrefs() {
  const { state, setState } = useLocalStorageState<AccessibilityPrefs>("bridge.a11y.v1", defaults);

  useEffect(() => {
    const root = document.documentElement;
    root.dataset.reducedMotion = state.reducedMotion ? "1" : "0";
    root.dataset.highReadability = state.highReadability ? "1" : "0";
    root.dataset.lowStimulation = state.lowStimulation ? "1" : "0";
    root.dataset.colorblindSafe = state.colorblindSafe ? "1" : "0";
  }, [state]);

  return { prefs: state, setPrefs: setState };
}

