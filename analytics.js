/* Fura — Google Analytics og Meta Pixel með cookie-samþykki.
   Báðar mælingar hlaðast AÐEINS eftir samþykki notanda. */
(function () {
  var GA_ID = 'G-PBCK2DB9V4';
  var META_PIXEL_ID = '1812480936617040';

  /* Nýr lykill: biðja þarf aftur um samþykki þar sem auglýsingamæling er ný. */
  var KEY = 'fura-cookie-consent-v2';

  function loadGA() {
    if (window.__furaGA) return;
    window.__furaGA = true;

    var script = document.createElement('script');
    script.async = true;
    script.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(script);

    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID);
  }

  function loadMetaPixel() {
    if (window.__furaMetaPixel) return;
    window.__furaMetaPixel = true;

    !function (f, b, e, v, n, t, s) {
      if (f.fbq) return;
      n = f.fbq = function () {
        n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments);
      };
      if (!f._fbq) f._fbq = n;
      n.push = n;
      n.loaded = true;
      n.version = '2.0';
      n.queue = [];
      t = b.createElement(e);
      t.async = true;
      t.src = v;
      s = b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t, s);
    }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

    window.fbq('init', META_PIXEL_ID);
    window.fbq('track', 'PageView');
  }

  function loadTracking() {
    loadGA();
    loadMetaPixel();
  }

  function readChoice() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function saveChoice(value) {
    try { localStorage.setItem(KEY, value); } catch (e) {}
  }

  function showBanner() {
    var lang = 'is';
    try { lang = sessionStorage.getItem('fura-lang') || 'is'; } catch (e) {}

    var text = (lang === 'en')
      ? {
          msg: 'We use optional cookies to measure traffic and show more relevant advertising. You can accept or decline them.',
          ok: 'Accept all',
          no: 'Decline'
        }
      : {
          msg: 'Við notum valfrjálsar vafrakökur til að mæla umferð og birta viðeigandi auglýsingar. Þú getur samþykkt eða hafnað þeim.',
          ok: 'Samþykkja allt',
          no: 'Hafna'
        };

    var css = document.createElement('style');
    css.textContent =
      '#fura-cc{position:fixed;left:0;right:0;bottom:0;z-index:9999;background:#1a1512;color:#fff;' +
      'padding:1rem 5%;display:flex;align-items:center;gap:1.25rem;flex-wrap:wrap;justify-content:center;' +
      "font-family:'Onest',-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif;" +
      'box-shadow:0 -4px 24px rgba(0,0,0,.25);animation:fura-cc-up .35s ease}' +
      '@keyframes fura-cc-up{from{transform:translateY(100%)}to{transform:translateY(0)}}' +
      '#fura-cc p{margin:0;font-size:.95rem;line-height:1.5;color:rgba(255,255,255,.85);max-width:720px}' +
      '#fura-cc .fura-cc-btns{display:flex;gap:.65rem;flex-shrink:0}' +
      '#fura-cc button{font:inherit;font-size:.9rem;font-weight:600;cursor:pointer;border-radius:6px;' +
      'padding:.6rem 1.3rem;border:1px solid transparent;transition:opacity .2s,background .2s,border-color .2s}' +
      '#fura-cc .fura-ok{background:#1a50a2;color:#fff}#fura-cc .fura-ok:hover{opacity:.9}' +
      '#fura-cc .fura-no{background:transparent;color:#fff;border-color:rgba(255,255,255,.4)}' +
      '#fura-cc .fura-no:hover{border-color:#fff}' +
      '@media(max-width:600px){#fura-cc{flex-direction:column;gap:.85rem;text-align:center}' +
      '#fura-cc .fura-cc-btns{width:100%}#fura-cc button{flex:1}}' +
      '@media(prefers-reduced-motion:reduce){#fura-cc{animation:none}}';
    document.head.appendChild(css);

    var bar = document.createElement('div');
    bar.id = 'fura-cc';
    bar.setAttribute('role', 'dialog');
    bar.setAttribute('aria-label', lang === 'en' ? 'Cookie settings' : 'Vafrakökustillingar');

    var message = document.createElement('p');
    message.textContent = text.msg;

    var controls = document.createElement('div');
    controls.className = 'fura-cc-btns';

    var decline = document.createElement('button');
    decline.type = 'button';
    decline.className = 'fura-no';
    decline.textContent = text.no;

    var accept = document.createElement('button');
    accept.type = 'button';
    accept.className = 'fura-ok';
    accept.textContent = text.ok;

    function close() {
      if (bar.parentNode) bar.parentNode.removeChild(bar);
    }

    decline.addEventListener('click', function () {
      saveChoice('denied');
      close();
    });

    accept.addEventListener('click', function () {
      saveChoice('granted');
      loadTracking();
      close();
    });

    controls.appendChild(decline);
    controls.appendChild(accept);
    bar.appendChild(message);
    bar.appendChild(controls);
    document.body.appendChild(bar);
  }

  function start() {
    var choice = readChoice();
    if (choice === 'granted') loadTracking();
    else if (choice !== 'denied') showBanner();
  }

  if (document.body) start();
  else document.addEventListener('DOMContentLoaded', start);
})();
