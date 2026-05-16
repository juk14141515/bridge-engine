import { Link } from 'react-router-dom';
import { PRODUCT_HERO_TITLE, PRODUCT_WELCOME_TAGLINE } from '../lib/productPitch';

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
        <h1 className="h1 welcome-title">{PRODUCT_HERO_TITLE}</h1>
        <p className="welcome-tagline muted">{PRODUCT_WELCOME_TAGLINE}</p>
      </section>

      <div className="instant-demo-grid">
        <div className="instant-demo-card card--warm">
          <div className="instant-demo-before">Paper</div>
          <div className="instant-demo-arrow" aria-hidden>
            →
          </div>
          <ul className="instant-demo-list">
            <li>Open a doc</li>
            <li>Write one rough part</li>
            <li>Add one source</li>
          </ul>
        </div>
        <div className="instant-demo-card card--warm">
          <div className="instant-demo-before">Coding path</div>
          <div className="instant-demo-arrow" aria-hidden>
            →
          </div>
          <ul className="instant-demo-list">
            <li>Name the &ldquo;spec&rdquo;</li>
            <li>Build one section</li>
            <li>Clean one draft pass</li>
          </ul>
        </div>
      </div>

      <div className="welcome-cta">
        <Link className="btn btn-primary btn-primary--welcome" to="/home">
          Continue
        </Link>
      </div>
    </>
  );
}
