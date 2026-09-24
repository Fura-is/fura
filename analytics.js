/* Fura — Google Analytics með cookie-samþykki (opt-in, GDPR-vænt)
   GA hleðst AÐEINS ef notandinn samþykkir. Valið er munað í localStorage. */
(function () {
  var GA_ID = 'G-4Z2JSQDWMC';
  var KEY = 'fura-cookie-consent';

  function loadGA() {
    if (window.__furaGA) return;
    window.__furaGA = true;
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID);
  }

  var choice = null;
  try { choice = localStorage.getItem(KEY); } catch (e) {}
  if (choice === 'granted') { loadGA(); return; }
  if (choice === 'denied') { return; }

  // Ekkert val enn -> sýna borða. Texti fylgir völdu tungumáli síðunnar.
  var lang = 'is';
  try { lang = sessionStorage.getItem('fura-lang') || 'is'; } catch (e) {}
  var T = (lang === 'en')
    ? { msg: 'We use cookies to measure traffic and improve the site.', ok: 'Accept', no: 'Decline' }
    : { msg: 'Við notum vafrakökur til að mæla umferð og bæta vefinn.', ok: 'Samþykkja', no: 'Hafna' };

  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function show() {
    var css = document.createElement('style');
    css.textContent =
      '#fura-cc{position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#1a1512;color:#fff;' +
      'padding:1rem 5%;display:flex;align-items:center;gap:1.25rem;flex-wrap:wrap;justify-content:center;' +
      "font-family:'Onest',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;" +
      'box-shadow:0 -4px 24px rgba(0,0,0,0.25);animation:fura-cc-up .35s ease}' +
      '@keyframes fura-cc-up{from{transform:translateY(100%)}to{transform:translateY(0)}}' +
      '#fura-cc p{margin:0;font-size:.95rem;line-height:1.5;color:rgba(255,255,255,.85);max-width:640px}' +
      '#fura-cc .fura-cc-btns{display:flex;gap:.65rem;flex-shrink:0}' +
      '#fura-cc button{font:inherit;font-size:.9rem;font-weight:600;cursor:pointer;border-radius:6px;padding:.6rem 1.3rem;border:1px solid transparent;transition:opacity .2s,background .2s,border-color .2s}' +
      '#fura-cc .fura-ok{background:#1a50a2;color:#fff}#fura-cc .fura-ok:hover{opacity:.9}' +
      '#fura-cc .fura-no{background:transparent;color:#fff;border-color:rgba(255,255,255,.4)}#fura-cc .fura-no:hover{border-color:#fff}' +
      '@media(max-width:600px){#fura-cc{flex-direction:column;gap:.85rem;text-align:center}#fura-cc .fura-cc-btns{width:100%}#fura-cc button{flex:1}}' +
      '@media(prefers-reduced-motion:reduce){#fura-cc{animation:none}}';
    document.head.appendChild(css);

    var bar = document.createElement('div');
    bar.id = 'fura-cc';
    bar.setAttribute('role', 'dialog');
    bar.setAttribute('aria-label', 'Vafrakökur');
    var p = document.createElement('p');
    p.textContent = T.msg;
    var wrap = document.createElement('div');
    wrap.className = 'fura-cc-btns';
    var no = document.createElement('button');
    no.className = 'fura-no'; no.textContent = T.no;
    var ok = document.createElement('button');
    ok.className = 'fura-ok'; ok.textContent = T.ok;
    wrap.appendChild(no); wrap.appendChild(ok);
    bar.appendChild(p); bar.appendChild(wrap);

    function close() { if (bar.parentNode) bar.parentNode.removeChild(bar); }
    ok.addEventListener('click', function () { save('granted'); loadGA(); close(); });
    no.addEventListener('click', function () { save('denied'); close(); });

    document.body.appendChild(bar);
  }

  if (document.body) show();
  else document.addEventListener('DOMContentLoaded', show);
})();
