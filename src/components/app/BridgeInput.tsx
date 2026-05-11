import { Field } from "../ui/Field";
import { TextArea } from "../ui/Input";

export function BridgeInput(props: { value: string; onChange: (v: string) => void }) {
  return (
    <Field label="What are you stuck on?" hint="Plain language is best.">
      <TextArea
        value={props.value}
        onChange={(e) => props.onChange(e.target.value)}
        placeholder="Example: “I need to study chemistry but I keep avoiding it.”"
        aria-label="Stuck input"
      />
    </Field>
  );
}

