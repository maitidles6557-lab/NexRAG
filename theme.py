"""Shared NexRAG visual theme for all Streamlit pages."""

import streamlit as st


def apply_theme():
    """Apply the responsive dark-glass NexRAG presentation."""
    st.markdown(
        r"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@300;400;500;600;700&display=swap');

        :root {
          --nx-bg: #05060f;
          --nx-panel: rgba(16, 19, 41, .78);
          --nx-border: rgba(110, 231, 183, .16);
          --nx-text: #eaf0ff;
          --nx-muted: #aeb9d6;
          --nx-violet: #22c55e;
          --nx-blue: #0ea57a;
          --nx-ease: cubic-bezier(.2,.7,.2,1);
          --nx-motion-fast: 160ms;
          --nx-motion: 220ms;
        }
        html, body, [class*="css"] { font-family: 'Urbanist', sans-serif; }
        html, body { min-width: 0; background: var(--nx-bg); scroll-behavior: smooth; }
        .stApp {
          position: relative;
          min-height: 100vh;
          color: var(--nx-text);
          background: #05060f !important;
          isolation: isolate;
        }
        .stApp::before {
          content: "";
          position: fixed;
          inset: 0;
          z-index: 0;
          pointer-events: none;
          background:
            radial-gradient(ellipse 60% 70% at 50% -8%, rgba(134, 239, 172, .35) 0%, rgba(34, 197, 94, .22) 25%, rgba(16, 120, 83, .12) 54%, transparent 76%),
            radial-gradient(ellipse 48% 43% at 91% 102%, rgba(16, 185, 129, .24), transparent 73%),
            radial-gradient(ellipse 42% 40% at 4% 102%, rgba(74, 222, 128, .18), transparent 74%);
        }
        .stApp > div { position: relative; z-index: 1; }
        [data-testid="stHeader"], [data-testid="stToolbar"], footer,
        section[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none !important; }
        [data-testid="stMainBlockContainer"], .block-container {
          width: 100% !important;
          max-width: 1100px !important;
          min-width: 0 !important;
          margin-inline: auto !important;
          padding: 26px 24px 54px 88px !important;
          box-sizing: border-box !important;
          position: relative;
          z-index: 1;
        }
        .block-container > div, [data-testid="stMain"] { min-width: 0; }
        .block-container, .block-container * { box-sizing: border-box; }
        .block-container { overflow-wrap: anywhere; }

        .st-key-app_shell { width: 100%; min-width: 0; }
        .st-key-rail {
          position: fixed !important;
          left: 16px !important;
          top: 16px !important;
          bottom: 16px !important;
          z-index: 50 !important;
          display: flex !important;
          flex-direction: column !important;
          align-items: center !important;
          gap: 12px !important;
          width: 56px !important;
          min-width: 56px !important;
          max-width: 56px !important;
          height: auto !important;
          padding: 10px 4px !important;
          overflow: visible !important;
          border: 0 !important;
          border-radius: 0 !important;
          background: transparent !important;
          box-shadow: none !important;
        }
        .st-key-workspace {
          width: 100% !important;
          max-width: 1120px !important;
          min-width: 0 !important;
          margin: 0 auto !important;
          padding: 0 !important;
        }
        .st-key-information {
          width: 100% !important;
          max-width: 1120px !important;
          min-width: 0 !important;
          margin: 28px auto 0 !important;
          padding: 0 !important;
        }
        /* Keep only the inner page widgets in tidy responsive rows. */
        .st-key-workspace [data-testid="stHorizontalBlock"] {
          display: flex !important;
          flex-direction: row !important;
          flex-wrap: nowrap !important;
          align-items: stretch !important;
          gap: 12px !important;
          width: 100% !important;
          min-width: 0 !important;
        }
        .st-key-workspace [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
          min-width: 0 !important;
          flex-shrink: 1 !important;
        }
        h1, h2, h3 { color: var(--nx-text); font-family: 'Urbanist', sans-serif !important; letter-spacing: -.02em; }
        p, label, [data-testid="stMarkdownContainer"] { color: #e3e9fb; }
        .nx-brand {
          position: relative;
          width: 48px;
          height: 48px;
          flex: 0 0 48px;
          overflow: visible;
          margin: 1px auto 18px;
          padding: 0;
          transform-style: preserve-3d;
          will-change: transform;
          animation: nx-brand-3d 6s ease-in-out infinite;
          filter: drop-shadow(0 0 12px rgba(34, 197, 94, .28));
          transition: filter var(--nx-motion) var(--nx-ease);
        }
        .nx-brand:hover { animation-duration: 2.8s; filter: brightness(1.16) drop-shadow(0 0 17px rgba(34, 197, 94, .45)); }
        .nx-brand svg {
          display: block;
          width: 48px !important;
          height: 48px !important;
          max-width: none !important;
          transform: translateZ(5px);
        }
        @keyframes nx-brand-3d {
          0%, 100% { transform: perspective(420px) rotateX(5deg) rotateY(-8deg) translateY(0); }
          50% { transform: perspective(420px) rotateX(-4deg) rotateY(8deg) translateY(-2px); }
        }
        .st-key-rail .nx-eyebrow,
        .st-key-rail .nx-rule,
        .st-key-rail .nx-recent,
        .st-key-rail .nx-status,
        .st-key-rail [data-testid="stCaptionContainer"],
        .st-key-rail [data-testid="stAlert"] { display: none !important; }
        .st-key-rail [data-testid="stButton"] {
          position: relative !important;
          width: 48px !important;
          height: 48px !important;
          flex: 0 0 48px !important;
          margin: 0 0 8px !important;
        }
        .st-key-rail [data-testid="stButton"] button {
          display: grid !important;
          place-items: center !important;
          width: 48px !important;
          min-width: 48px !important;
          max-width: 48px !important;
          height: 48px !important;
          min-height: 48px !important;
          padding: 0 !important;
          overflow: visible !important;
          border: 1px solid rgba(110,231,183,.08) !important;
          border-radius: 16px !important;
          color: transparent !important;
          background: rgba(11, 28, 23, .28) !important;
          box-shadow: inset 0 1px rgba(255,255,255,.025) !important;
          transition: transform 240ms var(--nx-ease), background-color var(--nx-motion) var(--nx-ease), border-color var(--nx-motion) var(--nx-ease), box-shadow var(--nx-motion) var(--nx-ease);
        }
        .st-key-rail [data-testid="stButton"] button p {
          width: 1px !important;
          height: 1px !important;
          overflow: hidden !important;
          white-space: nowrap !important;
          color: transparent !important;
          font-size: 1px !important;
          line-height: 1px !important;
        }
        .st-key-brand_toggle { margin: 2px 0 15px !important; }
        .st-key-brand_toggle button {
          border-color: rgba(110,231,183,.12) !important;
          background: rgba(11,28,23,.24) !important;
          box-shadow: 0 7px 20px rgba(0,0,0,.15), inset 0 1px rgba(255,255,255,.05) !important;
        }
        .st-key-brand_toggle button::before {
          content: "" !important;
          display: block;
          width: 34px;
          height: 34px;
          background-position: center;
          background-repeat: no-repeat;
          background-size: contain;
          filter: drop-shadow(0 0 7px rgba(52,211,153,.35));
          transition: transform 300ms var(--nx-ease), filter 300ms ease;
        }
        .st-key-brand_toggle button:hover::before { transform: rotate(-9deg) scale(1.08); filter: drop-shadow(0 0 12px rgba(52,211,153,.7)); }
        .nx-nav-collapsed-marker { display: none; }
        body:has(.nx-nav-collapsed-marker) [data-testid="stMainBlockContainer"],
        body:has(.nx-nav-collapsed-marker) .block-container { padding-left: 76px !important; }
        .st-key-nav_Home button::before { content: "\2302"; }
        .st-key-nav_Overview button::before { content: "\2726"; }
        .st-key-nav_Tools button::before { content: "\2692"; }
        .st-key-nav_History button::before { content: "\21BA"; }
        .st-key-nav_Contact button::before { content: "\2709"; }
        .st-key-nav_Contact { margin-top: auto !important; }
        .st-key-rail [data-testid="stButton"] button::before {
          display: block;
          grid-area: 1 / 1;
          place-self: center;
          width: 24px;
          height: 24px;
          margin: 0;
          color: #a9c7b6;
          font-size: 21px;
          font-family: 'Urbanist', sans-serif;
          line-height: 24px;
          text-align: center;
          font-weight: 400;
        }
        .st-key-brand_toggle button::before { width: 34px; height: 34px; line-height: 34px; }
        .st-key-rail [data-testid="stButton"]:hover button {
          transform: translateY(-3px) scale(1.06);
          border-color: rgba(110,231,183,.48) !important;
          background: linear-gradient(145deg, rgba(34,197,94,.3), rgba(15,159,117,.22)) !important;
          box-shadow: 0 8px 22px rgba(16,185,129,.22), inset 0 1px rgba(255,255,255,.14) !important;
        }
        .st-key-rail [data-testid="stButton"] button[kind="primary"] {
          border-color: rgba(167,243,208,.58) !important;
          background: linear-gradient(145deg, #22c55e, #087f5b) !important;
          box-shadow: 0 0 20px rgba(34, 197, 94, .34), inset 0 1px rgba(255,255,255,.3) !important;
          animation: nx-nav-select 360ms var(--nx-ease) both;
        }
        .st-key-rail [data-testid="stButton"] button[kind="primary"]::before { color: white !important; }
        .st-key-rail [class*="st-key-nav_"] { animation: nx-nav-enter 320ms var(--nx-ease) both; }
        .st-key-rail [class*="st-key-nav_"]:nth-of-type(3) { animation-delay: 35ms; }
        .st-key-rail [class*="st-key-nav_"]:nth-of-type(4) { animation-delay: 70ms; }
        .st-key-rail [class*="st-key-nav_"]:nth-of-type(5) { animation-delay: 105ms; }
        .st-key-rail [class*="st-key-nav_"]:nth-of-type(6) { animation-delay: 140ms; }
        @keyframes nx-nav-enter { from { opacity: 0; transform: translateX(-8px); } to { opacity: 1; transform: translateX(0); } }
        .st-key-nav_Home button:hover::after,
        .st-key-nav_Overview button:hover::after,
        .st-key-nav_Tools button:hover::after,
        .st-key-nav_History button:hover::after,
        .st-key-nav_Contact button:hover::after {
          position: absolute;
          left: 58px;
          top: 50%;
          z-index: 70;
          transform: translateY(-50%);
          padding: 7px 10px;
          border: 1px solid var(--nx-border);
          border-radius: 9px;
          color: white;
          background: rgba(14, 17, 38, .96);
          box-shadow: 0 8px 24px rgba(0,0,0,.3);
          font: 500 12px 'Urbanist', sans-serif;
          white-space: nowrap;
        }
        .st-key-nav_Home button:hover::after { content: "Home"; }
        .st-key-nav_Overview button:hover::after { content: "Overview"; }
        .st-key-nav_Tools button:hover::after { content: "Tools"; }
        .st-key-nav_History button:hover::after { content: "History"; }
        .st-key-nav_Contact button:hover::after { content: "Contact"; }
        @keyframes nx-nav-select {
          0% { transform: scale(.88); }
          65% { transform: scale(1.08); }
          100% { transform: scale(1); }
        }

        .nx-top-label { color: #c7cee5; font-size: 11px; font-weight: 600; letter-spacing: .12em; padding-top: 10px; white-space: nowrap; }
        .st-key-theme_toggle button { min-height: 40px !important; padding: 0 14px !important; border: 1px solid rgba(110,231,183,.3) !important; border-radius: 999px !important; color: #e5fff0 !important; background: linear-gradient(135deg,rgba(19,79,57,.72),rgba(8,51,43,.82)) !important; box-shadow: inset 0 1px rgba(255,255,255,.1),0 5px 18px rgba(0,0,0,.14) !important; transition: transform 220ms var(--nx-ease), box-shadow 260ms var(--nx-ease), background-color 300ms var(--nx-ease) !important; }
        .st-key-theme_toggle button::before { content: "\2600"; display: inline-block; margin-right: 8px; color: #a7f3d0; font-size: 17px; transition: transform 320ms var(--nx-ease), color 220ms ease; }
        .st-key-theme_toggle button:hover { transform: translateY(-2px); box-shadow: 0 8px 22px rgba(34,197,94,.2) !important; }
        .st-key-theme_toggle button:hover::before { transform: rotate(35deg) scale(1.12); }
        .st-key-theme_toggle button:active { transform: translateY(0) scale(.97); }
        .st-key-new_chat button { border: 1px solid rgba(110,231,183,.24) !important; background: rgba(14,47,35,.58) !important; transition: transform 220ms var(--nx-ease),background-color 240ms ease,border-color 240ms ease,box-shadow 240ms ease !important; }
        .st-key-new_chat button:hover { transform: translateY(-2px); border-color: rgba(110,231,183,.48) !important; background: linear-gradient(135deg,rgba(34,197,94,.26),rgba(15,159,117,.22)) !important; box-shadow: 0 8px 20px rgba(16,185,129,.18) !important; }
        .st-key-new_chat button:active { transform: translateY(0) scale(.98); }
        .st-key-new_chat button:focus-visible { outline: 2px solid rgba(110,231,183,.62) !important; outline-offset: 2px; }
        .nx-welcome { width: min(100%, 820px); margin: clamp(48px, 8vh, 92px) auto 32px; text-align: center; }
        .nx-welcome .nx-eyebrow { color: #d2d8ec; font-size: 11px; letter-spacing: .17em; }
        .nx-title {
          margin: 12px 0 10px;
          color: #fff;
          font: 300 clamp(2.4rem, 4.5vw, 3.6rem)/1.12 'Urbanist', sans-serif;
          letter-spacing: -.02em;
          background: linear-gradient(100deg, #fff 8%, rgba(239,244,255,.91) 55%, rgba(190,202,235,.52) 100%);
          background-clip: text;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          text-wrap: balance;
        }
        .nx-subtitle { max-width: 720px; margin: 0 auto; color: #c5cce0; font-size: 15px; line-height: 1.5; }
        .nx-subtitle-left { margin: 0 !important; text-align: left; }
        .nx-section-title { color: #eceeff; font: 600 14px 'Urbanist',sans-serif; letter-spacing: .02em; margin: 10px 0 9px; }
        .nx-rule { height: 1px; background: linear-gradient(90deg,transparent,rgba(186,194,238,.18),transparent); margin: 20px 0; }

        .nx-rag-stage { width: min(100%, 920px); margin: 4px auto 15px; isolation: isolate; }
        .nx-rag-visual { display: block; width: 100%; height: auto; overflow: visible; }
        .nx-rag-halo { fill: rgba(16,185,129,.025); stroke: rgba(110,231,183,.1); stroke-width: 1; stroke-dasharray: 2 9; }
        .nx-rag-path { fill: none; stroke: rgba(110,231,183,.48); stroke-width: 1.5; stroke-dasharray: 5 7; }
        .nx-doc-back { fill: rgba(18,88,64,.48); stroke: rgba(110,231,183,.36); stroke-width: 1.2; }
        .nx-doc-front { fill: url(#nx-glass); stroke: rgba(167,243,208,.72); stroke-width: 1.4; filter: drop-shadow(0 14px 20px rgba(0,0,0,.28)); }
        .nx-doc-fold { fill: none; stroke: rgba(167,243,208,.62); stroke-width: 1.3; }
        .nx-doc-line { fill: none; stroke: rgba(209,250,229,.76); stroke-width: 2; stroke-linecap: round; }
        .nx-doc-mark { fill: #34d399; filter: drop-shadow(0 0 6px rgba(52,211,153,.8)); }
        .nx-doc-stack { transform-origin: 115px 140px; animation: nx-doc-float 4.4s ease-in-out infinite; }
        .nx-core-sphere { fill: url(#nx-core-glow); filter: drop-shadow(0 0 27px rgba(52,211,153,.38)); animation: nx-core-pulse 4s ease-in-out infinite; }
        .nx-core-orbit { fill: none; stroke: rgba(167,243,208,.56); stroke-width: 1.25; stroke-dasharray: 4 6; transform-box: fill-box; transform-origin: center; animation: nx-core-spin 16s linear infinite; }
        .nx-core-network { fill: none; stroke: rgba(236,253,245,.68); stroke-width: 1.15; stroke-linecap: round; stroke-linejoin: round; animation: nx-network-glow 3s ease-in-out infinite; }
        .nx-core-dots circle { fill: #d1fae5; filter: drop-shadow(0 0 5px #34d399); animation: nx-dot-pulse 2s ease-in-out infinite; }
        .nx-core-dots circle:nth-child(2n) { animation-delay: .65s; }
        .nx-answer-card rect { fill: url(#nx-glass); stroke: rgba(167,243,208,.62); stroke-width: 1.3; filter: drop-shadow(0 12px 20px rgba(0,0,0,.26)); }
        .nx-answer-card { transform-origin: 730px 140px; animation: nx-answer-float 4s ease-in-out infinite; }
        .nx-answer-check { fill: rgba(52,211,153,.2); stroke: #6ee7b7; stroke-width: 1.3; }
        .nx-answer-tick { fill: none; stroke: #d1fae5; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
        .nx-answer-line { fill: none; stroke: rgba(209,250,229,.62); stroke-width: 2; stroke-linecap: round; }
        .nx-svg-label { fill: #a7f3d0; font: 600 11px 'Urbanist',sans-serif; letter-spacing: 2px; }
        .nx-flow-particle { fill: #d1fae5; }
        .nx-flow-particle-2 { fill: #6ee7b7; }
        @keyframes nx-doc-float { 0%,100% { transform: translateY(0) rotateY(-4deg); } 50% { transform: translateY(-7px) rotateY(4deg); } }
        @keyframes nx-answer-float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
        @keyframes nx-core-pulse { 0%,100% { filter: drop-shadow(0 0 21px rgba(52,211,153,.3)); } 50% { filter: drop-shadow(0 0 38px rgba(52,211,153,.58)); } }
        @keyframes nx-core-spin { to { transform: rotate(360deg); } }
        @keyframes nx-network-glow { 0%,100% { opacity: .58; } 50% { opacity: 1; } }
        @keyframes nx-dot-pulse { 0%,100% { opacity: .62; } 50% { opacity: 1; } }
        .nx-home-powers { position: relative; isolation: isolate; width: min(100%, 930px); margin: 0 auto 30px; display: flex; flex-wrap: wrap; align-items: center; justify-content: center; gap: 10px; }
        .nx-power-track { position: absolute; left: 7%; right: 7%; top: 50%; height: 1px; z-index: 0; background: linear-gradient(90deg,transparent,rgba(52,211,153,.12),rgba(167,243,208,.7),rgba(52,211,153,.12),transparent); background-size: 200% 100%; animation: nx-track-flow 4s linear infinite; }
        .nx-power-chip { position: relative; z-index: 1; display: inline-flex; align-items: center; gap: 8px; padding: 9px 12px; border: 1px solid rgba(110,231,183,.18); border-radius: 999px; color: #d6f5e5; background: rgba(7,20,18,.9); box-shadow: 0 5px 18px rgba(0,0,0,.16), inset 0 1px rgba(255,255,255,.04); font-size: 10px; font-weight: 600; letter-spacing: .015em; white-space: nowrap; animation: nx-chip-rise 4s ease-in-out infinite; }
        .nx-power-chip:nth-of-type(3) { animation-delay: .35s; }
        .nx-power-chip:nth-of-type(4) { animation-delay: .7s; }
        .nx-power-chip:nth-of-type(5) { animation-delay: 1.05s; }
        .nx-power-chip:nth-of-type(6) { animation-delay: 1.4s; }
        .nx-power-chip:hover { border-color: rgba(110,231,183,.5); box-shadow: 0 0 18px rgba(34,197,94,.16); }
        .nx-power-dot { width: 6px; height: 6px; flex: 0 0 6px; border-radius: 50%; background: #34d399; box-shadow: 0 0 10px rgba(52,211,153,.75); animation: nx-dot-beat 2s ease-in-out infinite; }
        @keyframes nx-track-flow { to { background-position: -200% 0; } }
        @keyframes nx-chip-rise { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-3px); } }
        @keyframes nx-dot-beat { 0%,100% { opacity: .55; transform: scale(.8); } 50% { opacity: 1; transform: scale(1.25); } }

        .st-key-prompt_card {
          width: 100%;
          min-width: 0;
          padding: 18px 18px 13px !important;
          border: 0 !important;
          border-radius: 25px !important;
          background: linear-gradient(112deg, rgba(16,150,91,.94), rgba(12,112,91,.92)) !important;
          box-shadow: 0 10px 30px rgba(16,150,91,.18), inset 0 1px rgba(255,255,255,.2) !important;
          transition: box-shadow var(--nx-motion) var(--nx-ease), border-color var(--nx-motion) var(--nx-ease);
        }
        .st-key-prompt_card:focus-within {
          box-shadow: 0 12px 34px rgba(16,150,91,.24), 0 0 0 3px rgba(110,231,183,.1) !important;
        }
        [data-baseweb="input"], [data-baseweb="base-input"],
        [data-testid="stTextInputRootElement"], [data-baseweb="textarea"],
        [data-testid="stTextAreaRootElement"] {
          border: 1px solid rgba(255,255,255,.14) !important;
          border-radius: 16px !important;
          background: rgba(255,255,255,.06) !important;
          box-shadow: none !important;
          transition: border-color var(--nx-motion) var(--nx-ease), box-shadow var(--nx-motion) var(--nx-ease), background-color var(--nx-motion) var(--nx-ease);
        }
        [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within,
        [data-testid="stTextInputRootElement"]:focus-within,
        [data-testid="stTextAreaRootElement"]:focus-within {
          border-color: rgba(110,231,183,.7) !important;
          box-shadow: 0 0 0 3px rgba(34,197,94,.14) !important;
        }
        [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea,
        input, textarea {
          min-width: 0 !important;
          color: #f5f6ff !important;
          background: rgba(255,255,255,.06) !important;
          border: 1px solid rgba(255,255,255,.14) !important;
          border-radius: 16px !important;
          outline: 0 !important;
          box-shadow: none !important;
        }
        input::placeholder, textarea::placeholder { color: #9da8c3 !important; opacity: 1; }
        input:-moz-autofill, input:-moz-autofill:focus,
        input:-webkit-autofill, input:-webkit-autofill:hover, input:-webkit-autofill:focus {
          -moz-appearance: none !important;
          -webkit-text-fill-color: #f5f6ff !important;
          caret-color: #f5f6ff !important;
          background-color: #101329 !important;
          box-shadow: 0 0 0 1000px #101329 inset !important;
          transition: background-color 999999s ease-out 0s !important;
        }
        .st-key-prompt_card [data-baseweb="input"],
        .st-key-prompt_card [data-baseweb="base-input"],
        .st-key-prompt_card [data-testid="stTextInputRootElement"],
        .st-key-prompt_card input,
        .st-key-prompt_card [data-baseweb="textarea"],
        .st-key-prompt_card [data-testid="stTextAreaRootElement"],
        .st-key-prompt_card textarea {
          min-width: 0 !important;
          border: 0 !important;
          border-radius: 0 !important;
          background: transparent !important;
          box-shadow: none !important;
        }
        .st-key-prompt_card input, .st-key-prompt_card textarea {
          min-height: 50px !important;
          padding-inline: 4px !important;
          color: white !important;
          font-size: 16px !important;
        }
        .st-key-prompt_card input::placeholder, .st-key-prompt_card textarea::placeholder { color: rgba(255,255,255,.82) !important; }
        .st-key-prompt_card [data-testid="stHorizontalBlock"] {
          display: flex !important;
          flex-wrap: nowrap !important;
          align-items: center !important;
          gap: 10px !important;
          min-width: 0 !important;
        }
        .st-key-prompt_card [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
          min-width: 0 !important;
          width: auto !important;
          max-width: none !important;
          padding: 0 !important;
        }
        .st-key-prompt_card [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child { flex: 1 1 auto !important; }
        .st-key-prompt_card [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2),
        .st-key-prompt_card [data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) { flex: 0 0 48px !important; }
        .st-key-prompt_card [data-testid="stButton"] button {
          width: 100% !important;
          min-width: 0 !important;
          min-height: 44px !important;
          border: 1px solid rgba(255,255,255,.3) !important;
          border-radius: 16px !important;
          color: #fff !important;
          background: rgba(255,255,255,.14) !important;
          box-shadow: inset 0 1px rgba(255,255,255,.14) !important;
          backdrop-filter: blur(9px);
        }
        .st-key-overview_composer_attach [data-testid="stFileUploader"],
        .st-key-chat_composer_attach [data-testid="stFileUploader"] {
          position: relative !important; width: 48px !important; height: 48px !important;
          min-width: 48px !important; min-height: 48px !important; overflow: hidden !important;
          border: 1px solid rgba(255,255,255,.3) !important; border-radius: 16px !important;
          background: #123d30 !important; box-shadow: inset 0 1px rgba(255,255,255,.12) !important;
        }
        .st-key-overview_composer_attach [data-testid="stFileUploader"] section,
        .st-key-chat_composer_attach [data-testid="stFileUploader"] section,
        .st-key-overview_composer_attach [data-testid="stFileUploaderDropzone"],
        .st-key-chat_composer_attach [data-testid="stFileUploaderDropzone"] {
          position: relative !important;
          width: 48px !important; height: 48px !important; min-height: 48px !important;
          padding: 0 !important; overflow: hidden !important; border: 0 !important;
          border-radius: 15px !important; background: transparent !important; cursor: pointer !important;
        }
        .st-key-overview_composer_attach [data-testid="stFileUploaderDropzoneInstructions"],
        .st-key-chat_composer_attach [data-testid="stFileUploaderDropzoneInstructions"],
        .st-key-overview_composer_attach [data-testid="stFileUploaderFile"],
        .st-key-chat_composer_attach [data-testid="stFileUploaderFile"],
        .st-key-overview_composer_attach [data-testid*="FileUploaderFile"],
        .st-key-chat_composer_attach [data-testid*="FileUploaderFile"],
        .st-key-overview_composer_attach [data-testid="stFileUploader"] svg,
        .st-key-chat_composer_attach [data-testid="stFileUploader"] svg { display: none !important; }
        .st-key-overview_composer_attach [data-testid="stFileUploader"] section > *,
        .st-key-chat_composer_attach [data-testid="stFileUploader"] section > *,
        .st-key-overview_composer_attach [data-testid="stFileUploaderDropzone"] > *,
        .st-key-chat_composer_attach [data-testid="stFileUploaderDropzone"] > * { visibility: hidden !important; }
        .st-key-overview_composer_attach [data-testid="stFileUploader"]::after,
        .st-key-chat_composer_attach [data-testid="stFileUploader"]::after {
          content: "+"; position: absolute; inset: 0; z-index: 10; display: grid; place-items: center;
          border-radius: inherit; color: #fff; background: #123d30;
          font: 400 24px/1 'Urbanist', sans-serif; pointer-events: none; visibility: visible !important;
        }
        .st-key-prompt_card .st-key-overview_composer_send button,
        .st-key-prompt_card .st-key-chat_composer_send button {
          width: 48px !important;
          height: 48px !important;
          min-height: 48px !important;
          border-radius: 16px !important;
          border: 1px solid rgba(255,255,255,.48) !important;
          background: linear-gradient(145deg,#34d399,#059669) !important;
          box-shadow: 0 4px 18px rgba(16,185,129,.3) !important;
          font-size: 20px !important;
        }
        .st-key-overview_composer_send button p, .st-key-chat_composer_send button p { white-space: nowrap !important; }

        .st-key-suggestions { margin: 14px 0 0 !important; }
        .st-key-suggestions [data-testid="stHorizontalBlock"] { gap: 12px !important; }
        .st-key-suggestions [data-testid="stColumn"] { min-width: 0 !important; }
        .st-key-suggestion_card_0, .st-key-suggestion_card_1, .st-key-suggestion_card_2 {
          height: 100%;
          min-height: 124px;
          padding: 17px 16px 13px !important;
          border: 1px solid rgba(211,220,255,.19) !important;
          border-radius: 24px !important;
          background: linear-gradient(145deg,rgba(223,230,255,.13),rgba(120,144,220,.065)) !important;
          box-shadow: inset 0 1px rgba(255,255,255,.08),0 8px 22px rgba(0,0,0,.13) !important;
          backdrop-filter: blur(8px);
          transition: transform var(--nx-motion) var(--nx-ease), border-color var(--nx-motion) var(--nx-ease), box-shadow var(--nx-motion) var(--nx-ease);
        }
        .st-key-suggestion_card_0:hover, .st-key-suggestion_card_1:hover, .st-key-suggestion_card_2:hover {
          transform: translateY(-2px);
          border-color: rgba(192,177,255,.38) !important;
          box-shadow: inset 0 1px rgba(255,255,255,.11),0 13px 26px rgba(30,35,95,.22) !important;
        }
        .st-key-suggestions [data-testid="stButton"] button {
          min-height: 38px;
          padding: 0 !important;
          border: 0 !important;
          border-radius: 9px !important;
          color: #f5f5ff !important;
          background: transparent !important;
          box-shadow: none !important;
          font-size: 15px !important;
          font-weight: 700 !important;
          text-align: left !important;
          justify-content: flex-start !important;
        }
        .st-key-suggestions [data-testid="stCaptionContainer"] p { color: #b8c0d5 !important; font-size: 11px !important; line-height: 1.45 !important; }

        .nx-card {
          height: 100%;
          min-height: 210px;
          padding: 17px 16px;
          border: 0;
          border-radius: 22px;
          background: linear-gradient(145deg,rgba(208,219,255,.075),rgba(101,123,198,.035));
          box-shadow: none;
          transition: transform var(--nx-motion) var(--nx-ease), background-color var(--nx-motion) var(--nx-ease);
        }
        .nx-card:hover { transform: translateY(-2px); background: rgba(52,211,153,.07); }
        .nx-card-label { color: #b5b9d0; font-size: 9px; font-weight: 700; letter-spacing: .12em; }
        .nx-card-title { color: #f5f4ff; font: 700 16px 'Urbanist',sans-serif; margin-top: 8px; overflow-wrap: anywhere; }
        .nx-card-copy { color: #b6bed2; font-size: 11px; line-height: 1.55; margin-top: 7px; }
        .st-key-tool_summary_card, .st-key-tool_images_card {
          height: 100%; padding: 20px; border-radius: 20px; background: rgba(16,35,29,.72);
          transition: transform 240ms var(--nx-ease), background-color 240ms ease, box-shadow 240ms ease;
          animation: nx-tool-enter 520ms var(--nx-ease) both;
        }
        .st-key-tool_images_card { animation-delay: 110ms; }
        .st-key-tool_summary_card:hover, .st-key-tool_images_card:hover {
          transform: translateY(-4px); background: rgba(18,54,41,.88); box-shadow: 0 18px 35px rgba(0,0,0,.18);
        }
        .nx-tool-art { width: 92px; height: 76px; margin: 2px 0 16px; display: grid; place-items: center; }
        .nx-tool-art svg { width: 88px; height: 70px; overflow: visible; }
        .nx-tool-page-back { fill: rgba(16,150,91,.18); stroke: rgba(110,231,183,.5); stroke-width: 1.4; }
        .nx-tool-page-front { fill: rgba(19,64,48,.92); stroke: #6ee7b7; stroke-width: 1.5; filter: drop-shadow(0 6px 8px rgba(0,0,0,.25)); }
        .nx-tool-page-fold { fill: none; stroke: #a7f3d0; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
        .nx-tool-spark { fill: #a7f3d0; filter: drop-shadow(0 0 5px #34d399); transform-origin: 77px 19px; animation: nx-tool-sparkle 2.4s ease-in-out infinite; }
        .nx-tool-summary-art svg { animation: nx-tool-document-float 3.5s ease-in-out infinite; }
        .nx-tool-image-frame { fill: rgba(8,34,27,.55); stroke: rgba(110,231,183,.68); stroke-width: 1.6; }
        .nx-tool-image-sun { fill: #a7f3d0; animation: nx-tool-sun 2.8s ease-in-out infinite; }
        .nx-tool-image-land { fill: rgba(52,211,153,.62); stroke: #6ee7b7; stroke-width: 1.3; stroke-linejoin: round; }
        .nx-tool-image-dot { fill: #d1fae5; filter: drop-shadow(0 0 4px #34d399); animation: nx-tool-dot 1.8s ease-in-out infinite; }
        .nx-tool-image-dot:last-child { animation-delay: .8s; }
        .nx-tool-images-art svg { animation: nx-tool-image-float 3.8s ease-in-out infinite; }
        .nx-tool-kicker { color: #86efac; font-size: 9px; font-weight: 700; letter-spacing: .14em; }
        .nx-tool-title { margin-top: 6px; color: #f2fff7; font: 700 20px 'Urbanist',sans-serif; }
        .nx-tool-copy { min-height: 42px; margin: 7px 0 16px; color: #bbd6c8; font-size: 12px; line-height: 1.55; }
        .nx-tool-result { margin: 20px 0; padding: 16px 0; border-top: 1px solid rgba(110,231,183,.12); }
        .nx-contact-card { position: relative; min-height: 208px; margin: 8px 0 14px; padding: 26px 22px 20px; overflow: hidden; border: 1px solid rgba(110,231,183,.2); border-radius: 22px; background: radial-gradient(circle at 100% 0%,rgba(52,211,153,.18),transparent 42%),linear-gradient(145deg,rgba(16,54,39,.86),rgba(12,23,34,.9)); box-shadow: inset 0 1px rgba(255,255,255,.07),0 14px 34px rgba(0,0,0,.18); animation: nx-contact-card-enter 520ms var(--nx-ease) both; }
        .nx-contact-card { transition: transform 320ms var(--nx-ease), border-color 320ms ease, box-shadow 320ms ease; }
        .nx-contact-card::after { content: ""; position: absolute; inset: -60% auto -60% -45%; width: 35%; transform: rotate(20deg); background: linear-gradient(90deg,transparent,rgba(236,253,245,.12),transparent); animation: nx-contact-sheen 7s ease-in-out infinite; pointer-events: none; }
        .nx-contact-card:hover { transform: translateY(-4px); border-color: rgba(110,231,183,.42); box-shadow: inset 0 1px rgba(255,255,255,.09),0 20px 42px rgba(0,0,0,.25),0 0 28px rgba(16,185,129,.1); }
        .nx-contact-card-icon { display: grid; width: 44px; height: 44px; place-items: center; margin-bottom: 18px; border: 1px solid rgba(110,231,183,.34); border-radius: 15px; color: #d1fae5; background: linear-gradient(145deg,rgba(34,197,94,.32),rgba(15,159,117,.2)); box-shadow: 0 6px 18px rgba(16,185,129,.16); font: 500 23px/1 'Urbanist',sans-serif; animation: nx-contact-icon-float 3.2s ease-in-out infinite; }
        .nx-contact-card-foot { display: flex; flex-wrap: wrap; gap: 8px 16px; margin-top: 18px; padding-top: 12px; border-top: 1px solid rgba(110,231,183,.14); color: #a9c7b6; font-size: 10px; letter-spacing: .035em; }
        .nx-contact-card-foot span::before { content: "\2713"; margin-right: 7px; color: #6ee7b7; }
        .nx-contact-email { display: flex; flex-direction: column; gap: 5px; margin: 14px 0; padding: 16px 18px; border: 1px solid rgba(110,231,183,.16); border-radius: 16px; background: linear-gradient(120deg,rgba(11,28,23,.48),rgba(12,31,25,.68)); transition: transform 240ms var(--nx-ease),border-color 240ms ease,box-shadow 240ms ease; }
        .nx-contact-email:hover { transform: translateY(-2px); border-color: rgba(110,231,183,.38); box-shadow: 0 10px 24px rgba(0,0,0,.16); }
        .nx-contact-email span { color: #86efac; font-size: 9px; font-weight: 700; letter-spacing: .14em; }
        .nx-contact-email a { width: fit-content; color: #e4fff0 !important; font-size: 14px; text-decoration: none; overflow-wrap: anywhere; }
        .nx-contact-email a:hover { color: #86efac !important; text-decoration: underline; }
        .st-key-contact_form_panel { min-height: 100%; padding: 24px !important; border: 1px solid rgba(110,231,183,.17) !important; border-radius: 24px !important; background: linear-gradient(145deg,rgba(12,31,25,.66),rgba(12,20,31,.76)) !important; box-shadow: inset 0 1px rgba(255,255,255,.05),0 14px 32px rgba(0,0,0,.15) !important; animation: nx-contact-panel-enter 680ms var(--nx-ease) 90ms both; }
        .nx-contact-form-heading { margin: 0 0 20px; padding-bottom: 18px; border-bottom: 1px solid rgba(110,231,183,.13); }
        .nx-contact-form-title { margin-top: 7px; color: #f2fff7; font: 700 22px 'Urbanist',sans-serif; letter-spacing: -.015em; }
        .nx-contact-form-copy { margin-top: 5px; color: #a9c7b6; font-size: 12px; line-height: 1.55; }
        .st-key-contact_form_panel .st-key-contact_message_form { padding: 0 !important; border: 0 !important; border-radius: 0 !important; background: transparent !important; box-shadow: none !important; animation: none !important; }
        .nx-account-intro { display: flex; align-items: center; gap: 17px; margin: 8px 0 14px; padding: 22px; border: 1px solid rgba(110,231,183,.18); border-radius: 22px; background: radial-gradient(circle at 100% 0%,rgba(52,211,153,.13),transparent 44%),linear-gradient(145deg,rgba(16,45,34,.74),rgba(12,20,31,.76)); animation: nx-contact-panel-enter 520ms var(--nx-ease) both; }
        .nx-account-intro-icon { display: grid; width: 52px; height: 52px; flex: 0 0 52px; place-items: center; border: 1px solid rgba(110,231,183,.3); border-radius: 17px; color: #c8f7dc; background: linear-gradient(145deg,rgba(34,197,94,.28),rgba(15,159,117,.16)); box-shadow: 0 7px 18px rgba(16,185,129,.13); font-size: 24px; }
        .nx-account-intro-title { margin-top: 4px; color: #f2fff7; font: 700 19px 'Urbanist',sans-serif; }
        .nx-account-intro-copy { margin-top: 4px; color: #a9c7b6; font-size: 12px; line-height: 1.5; }
        .st-key-contact_create_account, .st-key-contact_continue_email { padding: 22px !important; border: 1px solid rgba(110,231,183,.17) !important; border-radius: 21px !important; background: linear-gradient(145deg,rgba(12,31,25,.64),rgba(12,20,31,.74)) !important; box-shadow: inset 0 1px rgba(255,255,255,.04),0 12px 28px rgba(0,0,0,.14) !important; animation: nx-contact-panel-enter 560ms var(--nx-ease) both; }
        .nx-account-card { border: 1px solid rgba(110,231,183,.17); box-shadow: inset 0 1px rgba(255,255,255,.05),0 12px 28px rgba(0,0,0,.15); }
        @keyframes nx-contact-panel-enter { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
        .st-key-contact_message_form [data-testid="stFormSubmitButton"] button { transition: transform 220ms var(--nx-ease), box-shadow 260ms ease !important; }
        .st-key-contact_message_form [data-testid="stFormSubmitButton"] button:hover { transform: translateY(-2px); box-shadow: 0 9px 22px rgba(16,185,129,.24) !important; }
        @keyframes nx-contact-sheen { 0%,65%,100% { left: -45%; opacity: 0; } 72% { opacity: 1; } 92% { left: 125%; opacity: 0; } }
        @keyframes nx-contact-card-enter { from { opacity: 0; filter: blur(4px); } to { opacity: 1; filter: blur(0); } }
        @keyframes nx-contact-icon-float { 0%,100% { transform: translateY(0) rotate(0); } 50% { transform: translateY(-3px) rotate(-3deg); } }
        .nx-account-card { display: flex; align-items: center; gap: 16px; width: min(100%,560px); margin: 20px auto; padding: 20px; border-radius: 20px; background: rgba(16,35,29,.72); animation: nx-tool-enter 520ms var(--nx-ease) both; }
        .nx-account-avatar { display: grid; place-items: center; width: 54px; height: 54px; flex: 0 0 54px; border-radius: 50%; color: #eafff3; background: linear-gradient(145deg,#22c55e,#087f5b); font-size: 22px; font-weight: 700; box-shadow: 0 0 24px rgba(52,211,153,.25); }
        @keyframes nx-tool-enter { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes nx-tool-document-float { 0%,100% { transform: translateY(0) rotate(-1deg); } 50% { transform: translateY(-4px) rotate(1deg); } }
        @keyframes nx-tool-image-float { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-4px); } }
        @keyframes nx-tool-sparkle { 0%,100% { opacity: .65; transform: scale(.82) rotate(-12deg); } 50% { opacity: 1; transform: scale(1.12) rotate(12deg); } }
        @keyframes nx-tool-sun { 0%,100% { filter: drop-shadow(0 0 2px rgba(110,231,183,.3)); } 50% { filter: drop-shadow(0 0 8px rgba(110,231,183,.9)); } }
        @keyframes nx-tool-dot { 0%,100% { opacity: .5; transform: scale(.8); } 50% { opacity: 1; transform: scale(1.3); } }
        .nx-guide-card { min-height: 150px; margin-bottom: 12px; }
        .nx-guide-summary { min-height: 0; margin-bottom: 16px; padding: 16px 12px 8px; overflow: hidden; }
        .nx-history-doc, .nx-history-chat { min-height: 0; margin: 0 0 10px; animation: nx-history-enter 420ms var(--nx-ease) both; }
        .nx-history-doc:hover, .nx-history-chat:hover { border-color: rgba(110,231,183,.38); }
        .nx-history-excerpt { margin: 8px 0; padding: 12px 14px; border: 1px solid rgba(110,231,183,.15); border-radius: 12px; color: #c7dace; background: rgba(9,24,20,.65); font-size: 12px; line-height: 1.6; white-space: pre-wrap; overflow-wrap: anywhere; }
        .nx-history-excerpt b { color: #86efac; font-size: 10px; letter-spacing: .08em; text-transform: uppercase; }
        @keyframes nx-history-enter { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
        .nx-flow-diagram { display: block; width: 100%; height: auto; overflow: visible; }
        .nx-flow-rail { fill: none; stroke: url(#nx-flow-line); stroke-width: 2; stroke-linecap: round; stroke-dasharray: 4 5; }
        .nx-flow-node rect { fill: url(#nx-flow-card); stroke: rgba(110,231,183,.24); stroke-width: 1.2; }
        .nx-flow-icon { fill: none; stroke: #86efac; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
        .nx-flow-icon-fill { fill: #34d399; }
        .nx-flow-spark { fill: #a7f3d0; stroke: rgba(52,211,153,.7); stroke-width: 1; }
        .nx-flow-title { fill: #ecfdf5; font: 600 14px 'Urbanist',sans-serif; }
        .nx-flow-copy { fill: #a7cdbb; font: 400 10px 'Urbanist',sans-serif; }
        .nx-flow-caption { fill: #83ad97; font: 500 10px 'Urbanist',sans-serif; letter-spacing: .08em; }
        .nx-flow-pulse { fill: #d1fae5; filter: drop-shadow(0 0 5px #34d399); animation: nx-travel-flow 1.8s ease-in-out infinite; }
        .nx-flow-pulse-2 { animation-delay: .6s; }
        .nx-flow-pulse-3 { animation-delay: 1.2s; }
        @keyframes nx-travel-flow { 0% { opacity: .15; transform: translateX(0) scale(.8); } 55% { opacity: 1; transform: translateX(22px) scale(1.25); } 100% { opacity: .2; transform: translateX(30px) scale(.8); } }
        .nx-card-compact { min-height: unset !important; margin-bottom: 11px; }
        .nx-library-action { min-height: unset !important; }
        .st-key-card_Chat button, .st-key-card_Summarization button,
        .st-key-card_Tools button, .st-key-card_analyze button {
          width: 100% !important;
          min-height: 46px !important;
          white-space: nowrap !important;
        }

        [data-testid="stCheckbox"] input { accent-color: #22c55e !important; }
        [data-testid="stCheckbox"] [role="checkbox"] { border-color: rgba(176,184,230,.4) !important; border-radius: 6px !important; background: rgba(14,17,35,.75) !important; }
        [data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] { background: linear-gradient(135deg,#22c55e,#0f9f75) !important; border-color: #86efac !important; }
        [data-testid="stCheckbox"] [role="checkbox"][aria-checked="true"] svg { color: #fff !important; fill: #fff !important; }
        [data-testid="stTabs"] [role="tab"] { color: #abb3ce !important; transition: color .18s ease,border-color .18s ease; }
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: #fff !important; border-bottom-color: #34d399 !important; }
        [data-testid="stFileUploader"] section { border: 1px dashed rgba(110,231,183,.42) !important; border-radius: 18px !important; background: rgba(13,26,25,.74) !important; }
        [data-testid="stChatMessage"] { border: 0 !important; border-radius: 0 !important; background: transparent !important; padding-inline: 0 !important; }
        [data-testid="stExpander"] { border: 0 !important; border-radius: 10px !important; background: rgba(14,17,34,.34); }
        .st-key-home_chat_transcript [data-testid="stExpander"],
        .st-key-home_chat_transcript [data-testid="stExpander"] details,
        .st-key-home_chat_transcript [data-testid="stExpander"] summary,
        .st-key-home_chat_transcript [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
          border: 0 !important;
          outline: 0 !important;
          box-shadow: none !important;
        }
        .st-key-home_chat_transcript [data-testid="stExpander"] {
          display: inline-block !important;
          width: fit-content !important;
          max-width: min(100%, 460px) !important;
          padding-inline: 0 !important;
          background: transparent !important;
          vertical-align: top;
          transition: background-color 180ms ease, transform 180ms ease;
        }
        .st-key-home_chat_transcript [data-testid="stExpander"] details { width: fit-content !important; max-width: 100% !important; }
        .st-key-home_chat_transcript [data-testid="stExpander"]:hover,
        .st-key-home_chat_transcript [data-testid="stExpander"]:focus-within {
          background: rgba(52,211,153,.055) !important;
          transform: translateX(2px);
        }
        .nx-source-row {
          display: block;
          width: fit-content;
          max-width: 100%;
          margin: 3px 0;
          padding: 5px 8px;
          border-radius: 8px;
          color: var(--nx-text);
          text-align: left;
          line-height: 1.5;
          overflow-wrap: anywhere;
          transition: background-color 180ms ease, transform 180ms ease;
        }
        .nx-source-row:hover { background: rgba(52,211,153,.11); transform: translateX(3px); }
        .nx-source-row b { color: #86efac; }
        [data-testid="stAlert"] { border: 1px solid rgba(161,153,231,.24) !important; border-radius: 15px !important; background: rgba(23,25,48,.84) !important; color: #e8e8f5 !important; }
        [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p { color: #e1e2f1 !important; }
        [data-testid="stAlert"] svg { color: #86efac !important; }
        [data-testid="stSpinner"] p { color: #bbf7d0 !important; }
        [data-testid="stProgressBar"] div[role="progressbar"] { background: linear-gradient(90deg,#34d399,#15803d) !important; transition: width 280ms var(--nx-ease); }
        [data-testid="stButton"] button {
          border: 1px solid rgba(110,231,183,.2);
          border-radius: 13px;
          color: #f6f5ff;
          background: linear-gradient(135deg,rgba(16,150,91,.92),rgba(8,112,87,.92));
          box-shadow: 0 5px 16px rgba(16,120,83,.2);
          transition: transform var(--nx-motion-fast) var(--nx-ease), background-color var(--nx-motion) var(--nx-ease), color var(--nx-motion) var(--nx-ease), box-shadow var(--nx-motion) var(--nx-ease), border-color var(--nx-motion) var(--nx-ease);
        }
        [data-testid="stButton"] button:hover { transform: translateY(-1px); box-shadow: 0 8px 21px rgba(16,120,83,.28); border-color: rgba(110,231,183,.4); }
        [data-testid="stButton"] button:active { transform: translateY(0) scale(.985); }
        [data-testid="stButton"] button:focus-visible, input:focus-visible, textarea:focus-visible,
        [role="checkbox"]:focus-visible, [role="tab"]:focus-visible {
          outline: 2px solid rgba(110,231,183,.8) !important;
          outline-offset: 3px !important;
        }
        [data-testid="stButton"] button:disabled { opacity: .45; transform: none; box-shadow: none; }
        [data-testid="stButton"] button p { white-space: normal; overflow-wrap: anywhere; text-overflow: clip; }
        [data-testid="stButton"] button[kind="secondary"] { background: rgba(211,219,255,.08); box-shadow: none; }
        [data-testid="stDownloadButton"] button { border: 1px solid rgba(110,231,183,.3) !important; border-radius: 13px !important; color: #f1fff7 !important; background: linear-gradient(135deg,rgba(16,150,91,.92),rgba(8,112,87,.92)) !important; }
        .nx-empty { border: 0; border-radius: 20px; padding: 34px 22px; text-align: center; background: rgba(15,18,36,.32); }
        .nx-user-question { width: fit-content; max-width: min(82%, 720px); margin: 10px 2px 18px auto; padding: 10px 15px; border-radius: 18px 18px 4px 18px; color: #e8f7ef; background: rgba(30,125,86,.28); font-size: 14px; line-height: 1.55; white-space: pre-wrap; overflow-wrap: anywhere; }
        .st-key-home_chat_transcript { scrollbar-color: rgba(110,231,183,.35) transparent; scrollbar-width: thin; }
        .st-key-home_chat_transcript [data-testid="stChatMessage"] { padding-top: 4px !important; padding-bottom: 10px !important; }
        .nx-empty-title { color: #f7f5ff; font: 700 20px 'Urbanist',sans-serif; }
        .nx-empty-copy { color: #b4bad0; font-size: 13px; margin-top: 8px; }
        .nx-eyebrow { color: #86efac; font-size: 10px; font-weight: 700; letter-spacing: .15em; text-transform: uppercase; }
        .nx-recent { color: #c4cae0; font-size: 11px; line-height: 1.45; padding: 6px 0; overflow-wrap: anywhere; }
        .nx-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #43dca7; box-shadow: 0 0 10px rgba(67,220,167,.45); }
        .nx-dot-wait { background: #edb459; }
        .nx-dot-error { background: #ff7188; }
        [data-testid="stSpinner"] svg { animation-duration: 900ms !important; }
        .st-key-overview_composer_send button::before,
        .st-key-chat_composer_send button::before { content: "↑"; color: #fff; font-size: 22px; line-height: 1; }
        .st-key-overview_composer_send button p,
        .st-key-chat_composer_send button p { display: none !important; }

        @media (max-width: 900px) {
          [data-testid="stMainBlockContainer"], .block-container { padding-left: 82px !important; padding-right: 18px !important; }
          .st-key-workspace { max-width: 100% !important; }
          .nx-welcome { margin-top: 44px; }
        }
        @media (max-width: 700px) {
          .st-key-workspace [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
          .st-key-rail { display: none !important; }
          [data-testid="stMainBlockContainer"], .block-container { padding: 16px 14px 30px !important; }
          .st-key-contact_form_panel { padding: 18px 15px !important; }
          .nx-contact-card { padding: 22px 18px 18px; }
          .nx-account-intro { align-items: flex-start; padding: 18px 15px; }
          .st-key-contact_create_account, .st-key-contact_continue_email { padding: 17px 14px !important; }
          body:has(.nx-nav-collapsed-marker) [data-testid="stMainBlockContainer"],
          body:has(.nx-nav-collapsed-marker) .block-container { padding: 16px 14px 30px !important; }
          .st-key-workspace { width: 100% !important; max-width: 100% !important; }
          .nx-welcome { margin: 34px auto 22px; }
          .nx-title { font-size: clamp(2rem, 9vw, 3rem); }
          .nx-home-powers { gap: 7px; margin-bottom: 24px; }
          .nx-rag-stage { overflow-x: auto; }
          .nx-rag-visual { min-width: 580px; }
          .nx-power-track { display: none; }
          .nx-power-chip { font-size: 9px; padding: 8px 10px; }
          .nx-card { min-height: 190px; }
          .nx-guide-summary { overflow-x: auto; }
          .nx-flow-diagram { min-width: 650px; }
          .st-key-prompt_card { padding: 14px 12px 10px !important; border-radius: 23px !important; }
          .st-key-suggestions [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
          .st-key-suggestions [data-testid="stColumn"] { flex: 1 1 100% !important; width: 100% !important; }
        }
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; animation-duration: .01ms !important; }
          .nx-flow-pulse { animation: none !important; }
          .nx-home-powers *, .nx-home-powers *::before, .nx-home-powers *::after { animation: none !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.get("nx_theme", "dark") == "light":
        st.markdown(
            r"""
            <style>
            :root {
              color-scheme: light;
              --nx-bg: #e4ebe5;
              --nx-panel: rgba(239,244,239,.97);
              --nx-border: rgba(43,103,69,.19);
              --nx-text: #20372a;
              --nx-muted: #617368;
              --nx-light-accent: #38734d;
              --nx-light-accent-soft: #c9dacb;
              --nx-light-accent-line: rgba(43,103,69,.18);
            }
            html,body { background: var(--nx-bg) !important; color: var(--nx-text); transition: background-color 360ms ease,color 360ms ease; }
            .stApp { color: var(--nx-text) !important; background: #e4ebe5 !important; transition: background-color 360ms ease,color 360ms ease; }
            .stApp::before { background: radial-gradient(ellipse 62% 62% at 50% -10%,rgba(88,153,105,.11),transparent 74%),radial-gradient(ellipse 45% 42% at 96% 100%,rgba(52,116,73,.065),transparent 72%),radial-gradient(ellipse 40% 38% at 3% 100%,rgba(119,163,123,.07),transparent 74%) !important; }
            h1,h2,h3 { color: #20372a !important; }
            [data-testid="stMarkdownContainer"] p,label,[data-testid="stCheckbox"] label p { color: #314b39 !important; }
            [data-testid="stCaptionContainer"] p,.nx-subtitle,.nx-top-label { color: #5b7061 !important; }
            [data-testid="stSpinner"] p { color: #315d45 !important; }
            .nx-welcome .nx-eyebrow,.nx-eyebrow,.nx-tool-kicker,.nx-card-label,.nx-source-row b,.nx-history-excerpt b { color: #32704a !important; }
            .nx-title { background: linear-gradient(100deg,#183a28 8%,#315e3e 58%,#718c70 100%) !important; background-clip: text !important; -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; }
            .nx-section-title { color: #294b35 !important; }
            .nx-rule { background: linear-gradient(90deg,transparent,rgba(43,103,69,.22),transparent) !important; }
            [data-testid="stButton"] button p { color: #294b35 !important; }
            [data-testid="stButton"] button[kind="primary"] p,[data-testid="stFormSubmitButton"] button[kind="primary"] p { color: #fff !important; }
            .nx-card,.nx-empty,[data-testid="stChatMessage"],[data-testid="stExpander"],.nx-rail-card,.st-key-tool_summary_card,.st-key-tool_images_card { border-color: rgba(43,103,69,.17) !important; background: linear-gradient(145deg,rgba(247,250,246,.98),rgba(228,237,229,.98)) !important; box-shadow: inset 0 1px rgba(255,255,255,.74),0 8px 22px rgba(34,67,43,.07) !important; transition: background-color 300ms ease,border-color 280ms ease,box-shadow 280ms ease,color 300ms ease; }
            .nx-card:hover,.st-key-tool_summary_card:hover,.st-key-tool_images_card:hover { border-color: rgba(43,103,69,.3) !important; background: linear-gradient(145deg,#f7faf6,#e4eee5) !important; box-shadow: 0 10px 22px rgba(34,67,43,.1) !important; }
            [data-testid="stChatMessage"] { background: transparent !important; box-shadow: none !important; }
            [data-testid="stExpander"] { background: rgba(235,241,235,.8) !important; box-shadow: none !important; }
            .nx-card-title,.nx-empty-title,.nx-tool-title,.nx-contact-form-title,.nx-account-intro-title { color: #20372a !important; }
            .nx-card-copy,.nx-empty-copy,.nx-tool-copy,.nx-contact-form-copy,.nx-account-intro-copy,.nx-recent { color: #587064 !important; }
            .nx-user-question { color: #214c36 !important; background: rgba(52,132,82,.12) !important; border: 1px solid rgba(43,103,69,.12); }
            .nx-source-row { color: #365842 !important; border-color: rgba(43,103,69,.13) !important; }
            .nx-source-row b,.nx-history-excerpt b { color: #32704a !important; }
            .nx-history-excerpt { color: #355a42 !important; border-color: rgba(43,103,69,.16) !important; background: rgba(238,244,237,.98) !important; }
            .nx-contact-card { color: #244432 !important; border-color: rgba(43,103,69,.22) !important; background: radial-gradient(circle at 100% 0%,rgba(89,164,107,.13),transparent 44%),linear-gradient(145deg,rgba(225,239,226,.98),rgba(236,242,235,.98)) !important; box-shadow: inset 0 1px rgba(255,255,255,.7),0 12px 28px rgba(34,67,43,.08) !important; }
            .nx-contact-card::after { background: linear-gradient(90deg,transparent,rgba(255,255,255,.28),transparent) !important; }
            .nx-contact-card-icon,.nx-account-intro-icon { color: #28603c !important; border-color: rgba(43,103,69,.24) !important; background: linear-gradient(145deg,#d5e7d7,#bfd7c3) !important; box-shadow: 0 6px 15px rgba(38,105,60,.1) !important; }
            .nx-contact-card-foot { color: #567060 !important; border-color: rgba(43,103,69,.16) !important; }
            .nx-contact-card-foot span::before { color: #398153 !important; }
            .nx-contact-form-title { color: #20372a !important; }
            .nx-contact-form-copy { color: #587064 !important; }
            .st-key-contact_form_panel,.st-key-contact_create_account,.st-key-contact_continue_email { border-color: rgba(43,103,69,.17) !important; background: linear-gradient(145deg,rgba(247,250,246,.97),rgba(229,238,229,.97)) !important; box-shadow: inset 0 1px rgba(255,255,255,.74),0 12px 28px rgba(34,67,43,.07) !important; }
            .nx-contact-email { border-color: rgba(43,103,69,.18) !important; background: linear-gradient(120deg,#f6f9f5,#e7efe7) !important; }
            .nx-contact-email span { color: #32704a !important; }
            .nx-contact-email a { color: #284a34 !important; }
            .nx-account-intro { border-color: rgba(43,103,69,.18) !important; background: radial-gradient(circle at 100% 0%,rgba(89,164,107,.11),transparent 44%),linear-gradient(145deg,#f0f5ef,#e1ece2) !important; }
            .nx-account-card { color: #284a34 !important; border: 1px solid rgba(43,103,69,.17) !important; background: rgba(238,245,238,.96) !important; box-shadow: 0 9px 22px rgba(34,67,43,.08) !important; }
            .nx-account-avatar { color: #eff8f0 !important; background: linear-gradient(145deg,#4d9561,#287044) !important; box-shadow: 0 0 20px rgba(52,132,82,.18) !important; }
            .nx-account-intro-title { color: #20372a !important; }
            .nx-account-intro-copy { color: #587064 !important; }
            .st-key-contact_message_form [data-testid="stFormSubmitButton"] button:hover { box-shadow: 0 8px 18px rgba(36,111,62,.18) !important; }
            .st-key-contact_form_panel .st-key-contact_message_form { padding: 0 !important; border: 0 !important; border-radius: 0 !important; background: transparent !important; box-shadow: none !important; }
            [data-testid="stTextInputRootElement"],[data-testid="stTextAreaRootElement"],[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="textarea"],[data-testid="stSelectbox"] [data-baseweb="select"] > div { border-color: rgba(43,103,69,.2) !important; background: #f0f5ef !important; box-shadow: none !important; }
            [data-testid="stTextInput"] input,input,[data-testid="stTextArea"] textarea,textarea { color: #20372a !important; background: #f0f5ef !important; border-color: rgba(43,103,69,.2) !important; }
            input::placeholder,textarea::placeholder { color: #718176 !important; opacity: 1 !important; }
            [data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,[data-testid="stTextInputRootElement"]:focus-within,[data-testid="stTextAreaRootElement"]:focus-within { border-color: rgba(43,103,69,.55) !important; box-shadow: 0 0 0 3px rgba(52,132,82,.11) !important; }
            /* The prompt stays one surface: no white inset behind its text. */
            .st-key-prompt_card { background: linear-gradient(112deg,#cbdccd,#bdd2c0) !important; border: 1px solid rgba(43,103,69,.2) !important; box-shadow: 0 10px 26px rgba(34,67,43,.1),inset 0 1px rgba(255,255,255,.5) !important; }
            .st-key-prompt_card [data-testid="stTextInputRootElement"],.st-key-prompt_card [data-testid="stTextAreaRootElement"],.st-key-prompt_card [data-baseweb="input"],.st-key-prompt_card [data-baseweb="textarea"],.st-key-prompt_card [data-testid="stTextInput"] input,.st-key-prompt_card [data-testid="stTextArea"] textarea,.st-key-prompt_card input,.st-key-prompt_card textarea { color: #20372a !important; background: transparent !important; border: 0 !important; outline: 0 !important; box-shadow: none !important; }
            .st-key-prompt_card input::placeholder,.st-key-prompt_card textarea::placeholder { color: rgba(32,55,42,.66) !important; }
            .st-key-prompt_card:focus-within { box-shadow: 0 12px 30px rgba(34,67,43,.14),0 0 0 3px rgba(52,132,82,.1) !important; }
            .st-key-home_chat_input { border: 0 !important; outline: 0 !important; box-shadow: none !important; background: transparent !important; }
            .st-key-overview_composer_send button,.st-key-chat_composer_send button { color: white !important; background: linear-gradient(145deg,#4a9560,#287044) !important; border-color: rgba(43,103,69,.38) !important; box-shadow: 0 5px 15px rgba(36,111,62,.2) !important; }
            .st-key-overview_composer_send button::before,.st-key-chat_composer_send button::before { color: white !important; }
            .st-key-overview_composer_attach [data-testid="stFileUploader"],.st-key-chat_composer_attach [data-testid="stFileUploader"] { background: #2c7044 !important; border-color: rgba(43,103,69,.35) !important; box-shadow: 0 4px 12px rgba(36,111,62,.14) !important; }
            .st-key-overview_composer_attach [data-testid="stFileUploader"]::after,.st-key-chat_composer_attach [data-testid="stFileUploader"]::after { color: white !important; background: linear-gradient(145deg,#4a9560,#287044) !important; }
            .st-key-prompt_card input,.st-key-prompt_card textarea { color: #20372a !important; }
            .st-key-rail { border: 0 !important; background: transparent !important; box-shadow: none !important; }
            .st-key-rail [data-testid="stButton"] button { color: #355941 !important; border-color: rgba(43,103,69,.12) !important; background: rgba(243,248,242,.86) !important; box-shadow: 0 4px 12px rgba(34,67,43,.06) !important; }
            .st-key-rail [data-testid="stButton"] button::before { color: #386b49 !important; filter: none !important; }
            .st-key-rail [data-testid="stButton"] button:hover,.st-key-brand_toggle button:hover { border-color: rgba(43,103,69,.32) !important; background: rgba(213,231,215,.96) !important; box-shadow: 0 7px 18px rgba(34,93,53,.12) !important; }
            .st-key-rail [data-testid="stButton"] button[kind="primary"] { color: white !important; border-color: rgba(43,103,69,.42) !important; background: linear-gradient(145deg,#4a9560,#287044) !important; box-shadow: 0 0 16px rgba(52,132,82,.22),inset 0 1px rgba(255,255,255,.28) !important; }
            .st-key-rail [data-testid="stButton"] button[kind="primary"]::before { color: white !important; }
            .st-key-brand_toggle button { border-color: rgba(43,103,69,.12) !important; background: rgba(243,248,242,.78) !important; }
            .st-key-brand_toggle button::before { filter: none !important; }
            .st-key-theme_toggle button { color: #2e5f3d !important; border-color: rgba(43,103,69,.22) !important; background: linear-gradient(135deg,#f4f8f2,#e0ece1) !important; box-shadow: inset 0 1px rgba(255,255,255,.75),0 5px 16px rgba(34,67,43,.08) !important; }
            .st-key-theme_toggle button::before { color: #438258 !important; }
            .st-key-theme_toggle button:hover { box-shadow: 0 8px 20px rgba(36,111,62,.15) !important; }
            .st-key-new_chat button { color: #315c3e !important; border-color: rgba(43,103,69,.2) !important; background: linear-gradient(135deg,#f4f8f2,#e0ece1) !important; }
            .st-key-new_chat button:hover { color: #214b31 !important; border-color: rgba(43,103,69,.38) !important; background: linear-gradient(135deg,#dcebdd,#c8dfcb) !important; box-shadow: 0 7px 18px rgba(36,111,62,.14) !important; }
            .st-key-new_chat button:focus-visible { outline-color: rgba(43,103,69,.56) !important; }
            [data-testid="stButton"] button[kind="primary"],[data-testid="stFormSubmitButton"] button[kind="primary"],[data-testid="stLinkButton"] a[kind="primary"],[data-testid="stDownloadButton"] button { color: #fff !important; border-color: rgba(43,103,69,.3) !important; background: linear-gradient(135deg,#438b57,#287044) !important; box-shadow: 0 5px 14px rgba(36,111,62,.16),inset 0 1px rgba(255,255,255,.22) !important; }
            [data-testid="stButton"] button[kind="primary"] p,[data-testid="stFormSubmitButton"] button[kind="primary"] p,[data-testid="stDownloadButton"] p { color: #fff !important; }
            .stApp [data-testid="stFormSubmitButton"] button[kind="primary"],.stApp [data-testid="stLinkButton"] a[kind="primary"] { color: white !important; background: linear-gradient(135deg,#438b57,#287044) !important; }
            .stApp [data-testid="stFormSubmitButton"] button[kind="primary"] p { color: white !important; }
            .nx-home-powers .nx-power-chip { color: #31543b !important; border-color: rgba(43,103,69,.17) !important; background: rgba(242,247,240,.96) !important; box-shadow: 0 5px 14px rgba(34,67,43,.07) !important; }
            .nx-home-powers .nx-power-track { background: linear-gradient(90deg,transparent,rgba(80,151,96,.12),rgba(43,103,69,.46),rgba(80,151,96,.12),transparent) !important; background-size: 200% 100% !important; }
            .nx-power-dot,.nx-dot { background: #438258 !important; box-shadow: 0 0 8px rgba(52,132,82,.24) !important; }
            .nx-contact-email span { color: #32704a !important; }
            .nx-contact-email a { color: #284a34 !important; }
            .nx-account-intro-icon,.nx-contact-card-icon { color: #28603c !important; }
            .nx-contact-card-foot span::before { color: #398153 !important; }
            .nx-rag-halo { fill: rgba(52,132,82,.025) !important; stroke: rgba(43,103,69,.18) !important; }
            .nx-rag-path,.nx-doc-fold,.nx-doc-line,.nx-core-orbit,.nx-core-network,.nx-answer-line { stroke: rgba(43,103,69,.62) !important; }
            .nx-doc-back { fill: rgba(185,213,189,.72) !important; stroke: rgba(43,103,69,.48) !important; }
            .nx-doc-front,.nx-answer-card rect { fill: #eef4ed !important; stroke: rgba(43,103,69,.52) !important; filter: drop-shadow(0 9px 15px rgba(34,67,43,.14)) !important; }
            .nx-doc-mark,.nx-core-dots circle,.nx-flow-particle,.nx-flow-particle-2,.nx-answer-check { fill: #4c9560 !important; filter: drop-shadow(0 0 5px rgba(52,132,82,.25)) !important; }
            .nx-core-sphere { filter: drop-shadow(0 0 24px rgba(52,132,82,.24)) !important; }
            .nx-answer-tick { stroke: #287044 !important; }
            .nx-svg-label,.nx-flow-title,.nx-flow-copy,.nx-flow-caption { fill: #386348 !important; }
            .nx-flow-node rect { fill: #eef4ed !important; stroke: rgba(43,103,69,.3) !important; }
            .nx-flow-icon,.nx-flow-rail { stroke: #398153 !important; }
            .nx-flow-icon-fill,.nx-flow-spark { fill: #4c9560 !important; stroke: #287044 !important; }
            .nx-tool-page-back,.nx-tool-page-front,.nx-tool-image-frame { fill: #e7f0e7 !important; stroke: #4c9560 !important; }
            .nx-tool-page-fold,.nx-tool-image-land { stroke: #398153 !important; }
            .nx-tool-spark,.nx-tool-image-sun,.nx-tool-image-dot { fill: #4c9560 !important; filter: drop-shadow(0 0 4px rgba(52,132,82,.2)) !important; }
            .nx-svg-label { fill: #386348 !important; }
            [data-testid="stTabs"] [role="tab"] { color: #5c7061 !important; }
            [data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: #28603c !important; border-bottom-color: #4a9560 !important; }
            [data-testid="stAlert"] { border-color: rgba(43,103,69,.17) !important; background: rgba(239,245,238,.98) !important; color: #31543b !important; }
            [data-testid="stAlert"] [data-testid="stMarkdownContainer"] p { color: #31543b !important; }
            [data-testid="stDownloadButton"] p { color: #fff !important; }
            [data-testid="stCheckbox"] [role="checkbox"] { border-color: rgba(43,103,69,.32) !important; background: #f0f5ef !important; }
            .st-key-home_chat_transcript { scrollbar-color: rgba(43,103,69,.28) transparent; }
            [data-testid="stChatMessage"] img { filter: none !important; }
            @media (prefers-reduced-motion: reduce) { *,*::before,*::after { transition-duration: .01ms !important; animation-duration: .01ms !important; } }
            </style>
            """,
            unsafe_allow_html=True,
        )
