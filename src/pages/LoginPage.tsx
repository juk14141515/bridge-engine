import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const navigate = useNavigate();

  return (
    <div className="login-page">
      <h1 className="login-page__title">Sign in</h1>
      <p className="login-page__lede">
        Accounts will save sessions, sync workspaces, and preserve Bridge memory across devices.
      </p>
      <div className="login-page__panel">
        <button type="button" className="btn btn-primary btn-lg btn-block" disabled>
          Sign in
        </button>
        <button type="button" className="btn btn-quiet btn-lg btn-block" onClick={() => navigate('/start')}>
          Continue in dev mode
        </button>
      </div>
      <p className="muted small login-page__note">
        Dev mode does not pretend to secure data. It only lets you keep building locally.
      </p>
    </div>
  );
}
