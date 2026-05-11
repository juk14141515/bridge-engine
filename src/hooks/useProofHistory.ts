import type { ProofItem } from "../types/bridge";
import { nanoId } from "../lib/ids";
import { useLocalStorageState } from "./useLocalStorageState";

export function useProofHistory() {
  const { state, setState } = useLocalStorageState<ProofItem[]>("bridge.proofs.v1", []);

  function addProof(input: Omit<ProofItem, "id" | "createdAt">) {
    const next: ProofItem = { ...input, id: nanoId("proof"), createdAt: Date.now() };
    setState([next, ...state].slice(0, 100));
    return next;
  }

  function clearProofs() {
    setState([]);
  }

  return { proofs: state, addProof, clearProofs };
}

