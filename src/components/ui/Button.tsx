import { ButtonHTMLAttributes, ReactNode } from "react";
import styles from "./Button.module.css";

type Variant = "primary" | "ghost" | "danger";
type Size = "md" | "lg";

export function Button(
  props: ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: Variant;
    size?: Size;
    icon?: ReactNode;
  },
) {
  const { variant = "primary", size = "md", icon, className, ...rest } = props;
  return (
    <button
      {...rest}
      className={[
        styles.base,
        styles[variant],
        styles[size],
        rest.disabled ? styles.disabled : "",
        className ?? "",
      ].join(" ")}
    >
      {icon ? <span className={styles.icon} aria-hidden>{icon}</span> : null}
      <span className={styles.label}>{props.children}</span>
    </button>
  );
}

