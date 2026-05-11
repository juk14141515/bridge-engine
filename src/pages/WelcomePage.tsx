import { Link } from 'react-router-dom';

export default function WelcomePage() {
  return (
    <>
      <header className="top-bar">
        <span className="brand brand--soft">Bridge</span>
        <Link className="btn btn-quiet" to="/home">
          Skip
        </Link>
      </header>

      <section className="welcome-hero welcome-hero--tight">
        <h1 className="h1 welcome-title">Finish difficult things through what you already enjoy.</h1>
        <p className="welcome-tagline muted">
          Bridge is adaptive: a live workspace that senses momentum, rewrites steps when you need a
          gentler angle, grows a visible artifact, and saves every continuation—not generic productivity
          software.
        </p>
      </section>

      <div className="instant-demo-grid">
        <div className="instant-demo-card card--warm">
          <div className="instant-demo-before">Essay</div>
          <div className="instant-demo-arrow" aria-hidden>
            →
          </div>
          <ul className="instant-demo-list">
            <li>Open doc</li>
            <li>Messy paragraph</li>
            <li>One citation</li>
          </ul>
        </div>
        <div className="instant-demo-card card--warm">
          <div className="instant-demo-before">Gym</div>
          <div className="instant-demo-arrow" aria-hidden>
            →
          </div>
          <ul className="instant-demo-list">
            <li>Shoes on</li>
            <li>One minute move</li>
            <li>Optional extra rep</li>
          </ul>
        </div>
      </div>

      <div className="welcome-cta">
        <Link className="btn btn-primary btn-primary--welcome" to="/home">
          Enter Bridge
        </Link>
      </div>
    </>
  );
}
