import { InputHTMLAttributes, TextareaHTMLAttributes } from "react";
import styles from "./Input.module.css";

export function TextInput(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} className={[styles.base, props.className ?? ""].join(" ")} />;
}

export function TextArea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea {...props} className={[styles.base, styles.textarea, props.className ?? ""].join(" ")} />;
}

