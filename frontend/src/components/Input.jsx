import React, { useState } from "react";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import { marked } from "marked";

/* ─────────────────────────────────────────────────────
   1.  MARKED CONFIG  —  parse markdown → clean HTML
───────────────────────────────────────────────────── */
marked.setOptions({ breaks: true, gfm: true });

function parseMarkdown(raw = "") {
  // Strip bare `---` separators the backend often adds between sections
  const cleaned = raw.replace(/^---+$/gm, "").trim();
  return marked.parse(cleaned);
}

/* ─────────────────────────────────────────────────────
   2.  ALL STYLES  (injected once into <head>)
───────────────────────────────────────────────────── */
const Styles = () => (
  <style>{`
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    /* ── APP SHELL ── */
    .app {
      min-height: 100vh;
      background: #060d1a;
      padding: 52px 24px 80px;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }
    .app-header { text-align: center; margin-bottom: 44px; }
    .app-header h1 {
      font-family: 'Cormorant Garamond', serif;
      font-size: 42px;
      font-weight: 700;
      color: #fff;
      margin: 0 0 8px;
      letter-spacing: -0.5px;
    }
    .app-header p { color: #475569; font-size: 15px; margin: 0; }

    .input-row {
      display: flex;
      gap: 10px;
      max-width: 700px;
      margin: 0 auto 32px;
    }
    .url-input {
      flex: 1;
      padding: 14px 18px;
      background: #0f1f35;
      border: 1px solid #1e3a5f;
      border-radius: 10px;
      color: #e2e8f0;
      font-size: 14px;
      font-family: inherit;
      outline: none;
      transition: border-color .2s;
    }
    .url-input:focus { border-color: #38bdf8; }
    .url-input::placeholder { color: #334155; }
    .btn-gen {
      padding: 14px 26px;
      background: linear-gradient(135deg, #0e7490, #1d4ed8);
      color: #fff;
      border: none;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 600;
      font-family: inherit;
      cursor: pointer;
      white-space: nowrap;
      transition: opacity .2s, transform .15s;
    }
    .btn-gen:hover:not(:disabled) { opacity: .88; transform: translateY(-1px); }
    .btn-gen:disabled { opacity: .4; cursor: not-allowed; }

    .status { text-align: center; font-size: 13px; margin-bottom: 20px; }
    .status.err { color: #f87171; }
    .status.ok  { color: #4ade80; }

    .btn-dl {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0 auto 40px;
      padding: 13px 36px;
      background: #f59e0b;
      color: #0f172a;
      border: none;
      border-radius: 10px;
      font-size: 14px;
      font-weight: 700;
      font-family: inherit;
      cursor: pointer;
      transition: opacity .2s, transform .15s;
    }
    .btn-dl:hover { opacity: .88; transform: translateY(-1px); }
    .btn-dl:disabled { opacity: .5; cursor: not-allowed; }

    .preview-wrap {
      display: flex;
      justify-content: center;
    }
    .preview-shadow {
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 40px 100px rgba(0,0,0,.7), 0 0 0 1px rgba(255,255,255,.05);
      max-width: 860px;
      width: 100%;
    }

    .spinner {
      display: inline-block;
      width: 15px; height: 15px;
      border: 2px solid rgba(255,255,255,.25);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin .7s linear infinite;
      vertical-align: middle;
      margin-right: 6px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ════════════════════════════════════════════
       BROCHURE STYLES
    ════════════════════════════════════════════ */
    .brochure {
      width: 794px;
      background: #f8fafc;
      font-family: 'Plus Jakarta Sans', sans-serif;
      color: #1e293b;
    }

    /* ── COVER ── */
    .bc-cover {
      background: linear-gradient(145deg, #0a1628 0%, #0d2d5e 45%, #0c4a72 75%, #0e7490 100%);
      padding: 64px 56px 52px;
      position: relative;
      overflow: hidden;
    }
    .bc-cover-deco1 {
      position: absolute; top: -100px; right: -100px;
      width: 380px; height: 380px; border-radius: 50%;
      background: radial-gradient(circle, rgba(56,189,248,.18) 0%, transparent 70%);
      pointer-events: none;
    }
    .bc-cover-deco2 {
      position: absolute; bottom: -60px; left: 30%;
      width: 260px; height: 260px; border-radius: 50%;
      background: radial-gradient(circle, rgba(29,78,216,.25) 0%, transparent 70%);
      pointer-events: none;
    }
    .bc-eyebrow {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(245,158,11,.15);
      border: 1px solid rgba(245,158,11,.4);
      color: #fbbf24;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 2px;
      text-transform: uppercase;
      padding: 5px 14px;
      border-radius: 20px;
      margin-bottom: 24px;
      position: relative; z-index: 1;
    }
    .bc-eyebrow-dot {
      width: 5px; height: 5px;
      border-radius: 50%;
      background: #f59e0b;
    }
    .bc-cover h1 {
      font-family: 'Cormorant Garamond', serif;
      font-size: 54px;
      font-weight: 700;
      color: #fff;
      margin: 0 0 16px;
      line-height: 1.1;
      letter-spacing: -1px;
      position: relative; z-index: 1;
    }
    .bc-cover-rule {
      width: 64px; height: 4px;
      background: linear-gradient(90deg, #f59e0b, #fbbf24);
      border-radius: 2px;
      margin: 0 0 20px;
      position: relative; z-index: 1;
    }
    .bc-tagline {
      color: rgba(255,255,255,.6);
      font-size: 14px;
      margin: 0;
      position: relative; z-index: 1;
    }
    .bc-cover-badge {
      position: absolute;
      bottom: 28px; right: 48px;
      width: 68px; height: 68px;
      border-radius: 50%;
      background: rgba(255,255,255,.06);
      border: 1px solid rgba(255,255,255,.14);
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      z-index: 1;
    }
    .bc-badge-initials {
      font-family: 'Cormorant Garamond', serif;
      font-size: 20px;
      font-weight: 700;
      color: #fff;
      line-height: 1;
    }
    .bc-badge-year {
      font-size: 8px;
      color: rgba(255,255,255,.5);
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-top: 2px;
    }

    /* ── SECTION BANDS ── */
    .bc-section {
      padding: 36px 56px;
      border-bottom: 1px solid #e2e8f0;
    }
    .bc-section:last-of-type { border-bottom: none; }
    .bc-section-even { background: #ffffff; }
    .bc-section-odd  { background: #f8fafc; }

    /* ── HEADINGS INSIDE SECTIONS ── */
    .bc-section h2 {
      font-family: 'Cormorant Garamond', serif;
      font-size: 28px;
      font-weight: 700;
      color: #0d2d5e;
      margin: 0 0 6px;
      line-height: 1.2;
      letter-spacing: -.3px;
    }
    .h2-under {
      width: 44px; height: 3px;
      background: linear-gradient(90deg, #0e7490, #38bdf8);
      border-radius: 2px;
      margin-bottom: 20px;
    }
    .bc-section h3 {
      font-size: 11px;
      font-weight: 700;
      color: #0e7490;
      text-transform: uppercase;
      letter-spacing: 1.8px;
      margin: 22px 0 8px;
      padding-left: 10px;
      border-left: 3px solid #38bdf8;
    }

    /* ── BODY TEXT ── */
    .bc-section p {
      font-size: 14px;
      line-height: 1.85;
      color: #475569;
      margin: 0 0 14px;
    }

    /* ── LISTS ── */
    .bc-section ul {
      list-style: none;
      padding: 0;
      margin: 0 0 16px;
    }
    .bc-section ul li {
      font-size: 14px;
      line-height: 1.7;
      color: #475569;
      padding: 8px 0 8px 26px;
      position: relative;
      border-bottom: 1px solid #f1f5f9;
    }
    .bc-section ul li:last-child { border-bottom: none; }
    .bc-section ul li::before {
      content: '';
      position: absolute;
      left: 2px; top: 50%;
      transform: translateY(-50%);
      width: 8px; height: 8px;
      border-radius: 50%;
      background: linear-gradient(135deg, #0e7490, #38bdf8);
    }
    .bc-section ol {
      padding-left: 22px;
      margin: 0 0 16px;
    }
    .bc-section ol li {
      font-size: 14px;
      line-height: 1.7;
      color: #475569;
      margin-bottom: 6px;
    }
    .bc-section ol li::marker { color: #0e7490; font-weight: 700; }

    /* ── STRONG / EM ── */
    .bc-section strong { color: #1e293b; font-weight: 600; }
    .bc-section em { color: #0e7490; font-style: normal; font-weight: 500; }

    /* ── BLOCKQUOTE ── */
    .bc-section blockquote {
      background: linear-gradient(135deg, #eff6ff, #f0f9ff);
      border-left: 4px solid #0e7490;
      border-radius: 0 8px 8px 0;
      margin: 20px 0;
      padding: 16px 20px;
    }
    .bc-section blockquote p {
      color: #0d2d5e;
      font-style: italic;
      margin: 0;
    }

    /* ── FOOTER ── */
    .bc-footer {
      background: linear-gradient(90deg, #060d1a, #0d2d5e);
      padding: 24px 56px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .bc-footer-left { display: flex; align-items: center; gap: 12px; }
    .bc-footer-icon {
      width: 30px; height: 30px; border-radius: 50%;
      background: linear-gradient(135deg, #0e7490, #38bdf8);
      display: flex; align-items: center; justify-content: center;
      font-size: 10px; font-weight: 700; color: #fff;
      flex-shrink: 0;
    }
    .bc-footer-name { font-size: 13px; font-weight: 600; color: #fff; }
    .bc-footer-name span { color: #38bdf8; }
    .bc-footer-right { font-size: 11px; color: rgba(255,255,255,.3); letter-spacing: .5px; }
  `}</style>
);

/* ─────────────────────────────────────────────────────
   3.  SECTION WRAPPER  —  injects styled bands + h2 underlines
───────────────────────────────────────────────────── */
function buildSections(rawHtml) {
  const parts = rawHtml.split(/(?=<h2[\s>])/i).filter(Boolean);
  return parts
    .map((part, i) => {
      const withRule = part.replace(
        /(<h2[^>]*>.*?<\/h2>)/is,
        '$1<div class="h2-under"></div>'
      );
      const cls = i % 2 === 0 ? "bc-section bc-section-odd" : "bc-section bc-section-even";
      return `<div class="${cls}">${withRule}</div>`;
    })
    .join("");
}

/* ─────────────────────────────────────────────────────
   4.  BROCHURE LAYOUT COMPONENT
───────────────────────────────────────────────────── */
const Brochure = ({ html, companyName }) => {
  const year = new Date().getFullYear();
  const initials = (companyName || "CO")
    .split(/\s+/)
    .map((w) => w[0] || "")
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="brochure">
      {/* ── COVER ── */}
      <div className="bc-cover">
        <div className="bc-cover-deco1" />
        <div className="bc-cover-deco2" />
        <div className="bc-eyebrow">
          <div className="bc-eyebrow-dot" />
          Official Company Brochure
        </div>
        <h1>{companyName || "Company Overview"}</h1>
        <div className="bc-cover-rule" />
        <p className="bc-tagline">AI-generated company profile &nbsp;·&nbsp; {year}</p>
        <div className="bc-cover-badge">
          <div className="bc-badge-initials">{initials}</div>
          <div className="bc-badge-year">{year}</div>
        </div>
      </div>

      {/* ── BODY SECTIONS ── */}
      <div dangerouslySetInnerHTML={{ __html: buildSections(html) }} />

      {/* ── FOOTER ── */}
      <div className="bc-footer">
        <div className="bc-footer-left">
          <div className="bc-footer-icon">AI</div>
          <div className="bc-footer-name">
            {companyName
              ? <span>{companyName}</span>
              : <span>AI Brochure</span>}
          </div>
        </div>
        <div className="bc-footer-right">CONFIDENTIAL · {year}</div>
      </div>
    </div>
  );
};

/* ─────────────────────────────────────────────────────
   5.  PDF EXPORT  —  multi-page, full-bleed
───────────────────────────────────────────────────── */
async function exportPDF(elementId) {
  const el = document.getElementById(elementId);
  const canvas = await html2canvas(el, {
    scale: 2.5,
    useCORS: true,
    backgroundColor: "#f8fafc",
    logging: false,
    windowWidth: 794,
  });

  const pdf     = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
  const pageW   = pdf.internal.pageSize.getWidth();
  const pageH   = pdf.internal.pageSize.getHeight();
  const imgW    = pageW;
  const imgH    = (canvas.height * imgW) / canvas.width;
  const imgData = canvas.toDataURL("image/png");

  let yOffset = 0;
  while (yOffset < imgH) {
    if (yOffset > 0) pdf.addPage();
    pdf.addImage(imgData, "PNG", 0, -yOffset, imgW, imgH);
    yOffset += pageH;
  }

  pdf.save("brochure.pdf");
}

/* ─────────────────────────────────────────────────────
   6.  MAIN APP
───────────────────────────────────────────────────── */
export default function BrochureGenerator() {
  const [url,       setUrl]       = useState("");
  const [loading,   setLoading]   = useState(false);
  const [exporting, setExporting] = useState(false);
  const [html,      setHtml]      = useState("");
  const [company,   setCompany]   = useState("");
  const [status,    setStatus]    = useState({ type: "", msg: "" });

  const handleGenerate = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setStatus({ type: "", msg: "" });
    setHtml("");

    try {
      const res  = await fetch("http://127.0.0.1:50000/api/create-brochure", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ url }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Request failed");

      // Parse raw markdown → HTML
      const parsed = parseMarkdown(data.brochure);

      // Extract company name from first heading
      const match = parsed.match(/<h[12][^>]*>(.*?)<\/h[12]>/i);
      const name  = match
        ? match[1].replace(/<[^>]+>/g, "").split(/[–\-]/)[0].trim()
        : "";

      setCompany(name);
      setHtml(parsed);
      setStatus({ type: "ok", msg: "✓ Brochure ready — scroll down to preview" });
    } catch (e) {
      setStatus({ type: "err", msg: `⚠ ${e.message || "Failed to generate brochure"}` });
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    setExporting(true);
    await exportPDF("pdf-target");
    setExporting(false);
  };

  return (
    <>
      <Styles />
      <div className="app">
        <div className="app-header">
          <h1>AI Brochure Generator</h1>
          <p>Turn any website into a polished, print-ready company brochure</p>
        </div>
        <div className="input-row">
          <input
            className="url-input"
            type="text"
            placeholder="https://company.com"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !loading && handleGenerate()}
          />
          
          <button
            className="btn-gen"
            onClick={handleGenerate}
            disabled={loading || !url.trim()}
          >
            {loading && <span className="spinner" />}
            {loading ? "Generating…" : "Create Brochure"}
          </button>
        </div>

        {status.msg && (
          <p className={`status ${status.type}`}>{status.msg}</p>
        )}

        {html && !loading && (
          <>
            <button className="btn-dl" onClick={handleDownload} disabled={exporting}>
              {exporting
                ? <><span className="spinner" /> Exporting…</>
                : <>⬇ &nbsp;Download PDF</>}
            </button>

            <div className="preview-wrap">
              <div className="preview-shadow">
                <Brochure html={html} companyName={company} />
              </div>
            </div>
          </>
        )}
      </div>

      {/* Off-screen element captured by html2canvas for PDF */}
      <div
        id="pdf-target"
        style={{ position: "absolute", left: "-9999px", top: 0, width: "794px" }}
      >
        <Brochure html={html} companyName={company} />
      </div>
    </>
  );
}
