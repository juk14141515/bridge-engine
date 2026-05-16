import { useState } from "react";
import { apiClient, type AuthUser } from "../../lib/apiClient";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Field } from "../ui/Field";
import { TextInput } from "../ui/Input";
import styles from "./AuthSettings.module.css";

export function AuthSettings() {
  const [mode, setMode] = useState<"login" | "signup">("signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [user, setUser] = useState<AuthUser | null>(null);
  const [message, setMessage] = useState("");

  async function submit() {
    setMessage("");
    try {
      const result = mode === "signup" ? await apiClient.signup(email, password) : await apiClient.login(email, password);
      setUser(result.user);
      setMessage("Saved. This device can sync entry memory now.");
    } catch {
      setMessage("Could not connect. Local mode still works.");
    }
  }

  function signOut() {
    apiClient.clearToken();
    setUser(null);
    setMessage("Signed out locally.");
  }

  return (
    <Card title="Account" subtitle="Local mode works without this.">
      <div className={styles.stack}>
        {user ? (
          <>
            <div className={styles.user}>{user.email}</div>
            <Button variant="ghost" onClick={signOut}>
              Sign out
            </Button>
          </>
        ) : (
          <>
            <div className={styles.switcher}>
              <button className={styles.tab} type="button" onClick={() => setMode("signup")}>
                Sign up
              </button>
              <button className={styles.tab} type="button" onClick={() => setMode("login")}>
                Log in
              </button>
            </div>
            <Field label="Email">
              <TextInput value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            </Field>
            <Field label="Password" hint="6+ characters">
              <TextInput type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </Field>
            <Button onClick={submit}>{mode === "signup" ? "Create account" : "Log in"}</Button>
          </>
        )}
        {message ? <div className={styles.message}>{message}</div> : null}
      </div>
    </Card>
  );
}

