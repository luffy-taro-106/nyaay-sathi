"use client";

import { FormEvent, useCallback, useEffect, useMemo, useRef, useState, type MutableRefObject } from "react";

const LANGUAGE_OPTIONS = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "mr", label: "Marathi" },
  { code: "ta", label: "Tamil" },
  { code: "bn", label: "Bengali" },
];

const DEFAULT_BACKEND_URL = "http://127.0.0.1:8000";

function resolveBackendUrl(): string {
  const fromEnv = typeof process !== "undefined" ? process.env.NEXT_PUBLIC_BACKEND_URL : undefined;
  if (fromEnv?.trim()) return fromEnv.trim().replace(/\/$/, "");
  if (typeof window !== "undefined" && window.location?.hostname) {
    return `http://${window.location.hostname}:8000`;
  }
  return DEFAULT_BACKEND_URL;
}
const SESSION_STORAGE_KEY = "nyaay_session_id";

type OrchestrateResult = {
  disclaimer: string;
  category: string;
  crisis_detected: boolean;
  rights_summary: string;
  suggested_forum: string[];
  required_documents: string[];
  limitation_hint: string;
  free_legal_aid: string[];
  complaint_template: string;
  helplines: string[];
  needs_clarification: boolean;
  clarifying_questions: string[];
  session_id: string;
};

type ChatHistMsg = {
  role: "user" | "assistant";
  content: string;
  created_at: string;
  category?: string | null;
};

type SpeechRecognitionCtor = new () => {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
};
type SpeechRecognitionInstance = InstanceType<SpeechRecognitionCtor>;

function speakText(text: string, lang: string) {
  if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang === "hi" ? "hi-IN" : lang === "mr" ? "mr-IN" : lang === "ta" ? "ta-IN" : lang === "bn" ? "bn-IN" : "en-IN";
  utterance.rate = 1.4;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

function joinWithAnd(items: string[]): string {
  if (items.length === 0) return "";
  if (items.length === 1) return items[0]!;
  if (items.length === 2) return `${items[0]} and ${items[1]}`;
  return `${items.slice(0, -1).join(", ")}, and ${items[items.length - 1]}`;
}

/** Full voice script: summary plus forums, documents, and limits in connected prose (not only the summary block). */
function buildSpokenGuidance(data: OrchestrateResult, lang: string): string {
  let spoken = data.rights_summary.replace(/\s+/g, " ").trim();
  if (data.needs_clarification && data.clarifying_questions.length > 0) {
    spoken += " " + data.clarifying_questions.slice(0, 3).join(" ");
  } else {
    const bridges: string[] = [];
    if (data.suggested_forum.length > 0) {
      if (lang === "en") {
        bridges.push(`You could try ${joinWithAnd(data.suggested_forum)}.`);
      } else {
        bridges.push(data.suggested_forum.join(". ") + ".");
      }
    }
    if (data.required_documents.length > 0) {
      const docs = data.required_documents.slice(0, 6);
      if (lang === "en") {
        bridges.push(`It helps to have ${joinWithAnd(docs)} ready.`);
      } else {
        bridges.push(docs.join(", ") + ".");
      }
    }
    const hint = data.limitation_hint.trim();
    if (hint) {
      bridges.push(lang === "en" ? `On deadlines: ${hint}` : hint);
    }
    if (bridges.length) spoken += " " + bridges.join(" ");
  }
  if (data.crisis_detected && data.helplines.length > 0) {
    spoken += " If you need immediate help, helplines include " + joinWithAnd(data.helplines) + ".";
  }
  return spoken;
}

function unlockWebAudio(ctxRef: MutableRefObject<AudioContext | null>) {
  if (typeof window === "undefined") return;
  const win = window as unknown as { AudioContext?: typeof AudioContext; webkitAudioContext?: typeof AudioContext };
  const AC = win.AudioContext ?? win.webkitAudioContext;
  if (!AC) return;
  if (!ctxRef.current) {
    ctxRef.current = new AC();
  }
  void ctxRef.current.resume();
}

export default function Page() {
  const [backendUrl, setBackendUrl] = useState(DEFAULT_BACKEND_URL);
  const [language, setLanguage] = useState("en");
  const [district, setDistrict] = useState("Pune");
  const [message, setMessage] = useState("My employer has not paid wages for 3 months.");
  const [loading, setLoading] = useState(false);
  const [voiceListening, setVoiceListening] = useState(false);
  const [voiceWorking, setVoiceWorking] = useState(false);
  const [voiceLastHeard, setVoiceLastHeard] = useState("");
  const [pdfLoading, setPdfLoading] = useState(false);
  const [orchestrateResult, setOrchestrateResult] = useState<OrchestrateResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isClient, setIsClient] = useState(false);
  const [sessionId, setSessionId] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatHistMsg[]>([]);

  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const ttsSourceRef = useRef<AudioBufferSourceNode | null>(null);
  /** Bumped to cancel in-flight TTS fetch/decode/play when user taps the mic again. */
  const ttsEpochRef = useRef(0);
  const ttsFetchAbortRef = useRef<AbortController | null>(null);
  /** Always send the latest UI language (avoids stale closure on voice callbacks). */
  const languageRef = useRef(language);
  useEffect(() => {
    languageRef.current = language;
  }, [language]);

  type TtsResult = { played: boolean; useBrowserFallback: boolean };

  function stopTtsPlayback() {
    ttsEpochRef.current += 1;
    ttsFetchAbortRef.current?.abort();
    ttsFetchAbortRef.current = null;
    try {
      ttsSourceRef.current?.stop();
    } catch {
      /* already stopped */
    }
    ttsSourceRef.current = null;
    if (typeof window !== "undefined" && window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
  }

  const canUseBrowserVoice = useMemo(() => {
    if (!isClient) return null;
    return Boolean(
      (window as unknown as { webkitSpeechRecognition?: SpeechRecognitionCtor; SpeechRecognition?: SpeechRecognitionCtor }).webkitSpeechRecognition ||
        (window as unknown as { webkitSpeechRecognition?: SpeechRecognitionCtor; SpeechRecognition?: SpeechRecognitionCtor }).SpeechRecognition
    );
  }, [isClient]);

  useEffect(() => {
    setIsClient(true);
    setBackendUrl(resolveBackendUrl());
  }, []);

  const refreshHistory = useCallback(
    async (sid: string) => {
      try {
        const res = await fetch(`${backendUrl}/v1/chat/${encodeURIComponent(sid)}/history`);
        if (!res.ok) return;
        setChatHistory((await res.json()) as ChatHistMsg[]);
      } catch {
        /* ignore */
      }
    },
    [backendUrl],
  );

  useEffect(() => {
    if (!isClient) return;
    const saved = localStorage.getItem(SESSION_STORAGE_KEY);
    if (saved && saved.length >= 8) setSessionId(saved);
  }, [isClient]);

  useEffect(() => {
    if (!isClient) return;
    if (!sessionId) {
      setChatHistory([]);
      return;
    }
    void refreshHistory(sessionId);
  }, [isClient, sessionId, refreshHistory]);

  function startNewConversation() {
    setSessionId("");
    setChatHistory([]);
    setOrchestrateResult(null);
    if (typeof localStorage !== "undefined") localStorage.removeItem(SESSION_STORAGE_KEY);
  }

  async function speakWithServerTTS(text: string): Promise<TtsResult> {
    ttsFetchAbortRef.current?.abort();
    const epoch = ++ttsEpochRef.current;
    const ac = new AbortController();
    ttsFetchAbortRef.current = ac;
    try {
      const res = await fetch(`${backendUrl}/v1/tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, language: languageRef.current }),
        signal: ac.signal,
      });
      if (!res.ok) return { played: false, useBrowserFallback: true };
      const ctx = audioCtxRef.current;
      if (!ctx) return { played: false, useBrowserFallback: true };

      const arrayBuffer = await res.arrayBuffer();
      if (epoch !== ttsEpochRef.current) return { played: false, useBrowserFallback: false };
      const audioBuffer = await ctx.decodeAudioData(arrayBuffer.slice(0));
      if (epoch !== ttsEpochRef.current) return { played: false, useBrowserFallback: false };

      try {
        ttsSourceRef.current?.stop();
      } catch {
        /* ignore */
      }
      const src = ctx.createBufferSource();
      src.buffer = audioBuffer;
      src.connect(ctx.destination);
      ttsSourceRef.current = src;
      src.onended = () => {
        ttsSourceRef.current = null;
      };
      src.start();
      return { played: true, useBrowserFallback: false };
    } catch (err) {
      const aborted =
        (err instanceof DOMException && err.name === "AbortError") ||
        (err instanceof Error && err.name === "AbortError");
      if (aborted) return { played: false, useBrowserFallback: false };
      return { played: false, useBrowserFallback: true };
    } finally {
      if (ttsFetchAbortRef.current === ac) {
        ttsFetchAbortRef.current = null;
      }
    }
  }

  async function callOrchestrate(inputMessage: string) {
    const lang = languageRef.current;
    const res = await fetch(`${backendUrl}/v1/orchestrate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: inputMessage,
        language: lang,
        district,
        ...(sessionId ? { session_id: sessionId } : {}),
      }),
    });
    const raw = await res.text();
    if (!res.ok) {
      let detail = raw.slice(0, 240);
      try {
        const errBody = JSON.parse(raw) as { detail?: unknown };
        if (typeof errBody?.detail === "string") detail = errBody.detail;
        else if (Array.isArray(errBody?.detail))
          detail = errBody.detail.map((d) => JSON.stringify(d)).join("; ").slice(0, 240);
      } catch {
        /* keep raw slice */
      }
      throw new Error(`HTTP ${res.status}${detail ? `: ${detail}` : ""}`);
    }
    const data = JSON.parse(raw) as OrchestrateResult;
    if (data.session_id) {
      setSessionId(data.session_id);
      if (typeof localStorage !== "undefined") {
        localStorage.setItem(SESSION_STORAGE_KEY, data.session_id);
      }
      await refreshHistory(data.session_id);
    }
    return data;
  }

  async function handleVoiceTurn(transcript: string) {
    setVoiceWorking(true);
    setError(null);
    try {
      const data = await callOrchestrate(transcript);
      setOrchestrateResult(data);

      const lang = languageRef.current;
      const spoken = buildSpokenGuidance(data, lang);
      const tts = await speakWithServerTTS(spoken);
      if (tts.useBrowserFallback) {
        speakText(spoken, lang);
      }
    } catch {
      setError("Voice request failed. Please check backend and try again.");
    } finally {
      setVoiceWorking(false);
    }
  }

  function startVoiceListening() {
    if (!canUseBrowserVoice) {
      setError("Browser voice recognition is not supported in this browser. Use Chrome/Edge.");
      return;
    }
    setError(null);
    stopTtsPlayback();
    try {
      recognitionRef.current?.stop();
    } catch {
      /* ignore */
    }
    recognitionRef.current = null;
    unlockWebAudio(audioCtxRef);

    const win = window as unknown as {
      webkitSpeechRecognition?: SpeechRecognitionCtor;
      SpeechRecognition?: SpeechRecognitionCtor;
    };
    const Ctor = win.webkitSpeechRecognition ?? win.SpeechRecognition;
    if (!Ctor) return;

    const rec = new Ctor();
    recognitionRef.current = rec;
    rec.lang =
      languageRef.current === "hi"
        ? "hi-IN"
        : languageRef.current === "mr"
          ? "mr-IN"
          : languageRef.current === "ta"
            ? "ta-IN"
            : languageRef.current === "bn"
              ? "bn-IN"
              : "en-IN";
    rec.continuous = false;
    rec.interimResults = false;

    rec.onresult = (event) => {
      const transcript = event.results[0][0].transcript.trim();
      setVoiceLastHeard(transcript);
      setMessage(transcript);
      void handleVoiceTurn(transcript);
    };
    rec.onerror = (event) => {
      setError(`Voice error: ${event.error}`);
      setVoiceListening(false);
    };
    rec.onend = () => {
      setVoiceListening(false);
    };

    rec.start();
    setVoiceListening(true);
  }

  function stopVoiceListening() {
    recognitionRef.current?.stop();
    setVoiceListening(false);
  }

  async function runOrchestrate(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await callOrchestrate(message);
      setOrchestrateResult(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(
        msg.startsWith("HTTP")
          ? `/v1/orchestrate failed (${msg}). Is the backend running on ${backendUrl}? See .backend.log if you use run_product.sh.`
          : `Unable to reach /v1/orchestrate (${msg}). Check that the backend is running (try ${backendUrl}/health) and NEXT_PUBLIC_BACKEND_URL if you use a custom API host.`,
      );
    } finally {
      setLoading(false);
    }
  }

  async function downloadPdf() {
    setPdfLoading(true);
    setError(null);
    try {
      const res = await fetch(`${backendUrl}/v1/complaint-pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          language,
          district,
          ...(sessionId ? { session_id: sessionId } : {}),
        }),
      });
      if (!res.ok) {
        setError("PDF generation failed.");
        return;
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "nyaay-sathi-complaint.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      setError("PDF generation request failed.");
    } finally {
      setPdfLoading(false);
    }
  }

  const voiceStatusLabel =
    canUseBrowserVoice === null
      ? "Checking microphone access…"
      : canUseBrowserVoice
        ? voiceListening
          ? "Listening — speak naturally"
          : voiceWorking
            ? "Thinking…"
            : "Ready to listen"
        : "Voice not supported in this browser";

  const voiceStatusKind =
    canUseBrowserVoice === false ? "bad" : voiceListening ? "warn" : "ok";

  const categoryLabel = orchestrateResult
    ? formatCategory(orchestrateResult.category)
    : "";

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <span className="brand-name">Nyaay Sathi</span>
          <span className="brand-suffix">· legal companion</span>
        </div>
        <div className="topbar-actions">
          <div
            className="segmented"
            role="group"
            aria-label="Response language"
          >
            {LANGUAGE_OPTIONS.map((lang) => (
              <button
                key={lang.code}
                type="button"
                className="seg-item"
                aria-pressed={language === lang.code}
                onClick={() => setLanguage(lang.code)}
              >
                {lang.label}
              </button>
            ))}
          </div>
          <button
            type="button"
            className="btn btn--ghost btn--sm"
            onClick={startNewConversation}
            title="Start a new conversation"
          >
            New thread
          </button>
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <div>
            <span className="eyebrow">Voice-first legal navigator</span>
            <h1>
              Plain-language law,
              <br />
              <em>spoken back to you.</em>
            </h1>
            <p className="lede">
              Tap once and tell Nyaay Sathi what happened — wages held, an eviction notice,
              a refund denied, an FIR refused. We&rsquo;ll walk through where to go, what to
              gather, and how to start, in your language, on your terms.
            </p>
            <div className="capability-row" aria-label="Coverage">
              <span className="capability"><IconBriefcase /> Wages &amp; work</span>
              <span className="capability"><IconHome /> Rent &amp; property</span>
              <span className="capability"><IconShield /> Women&rsquo;s safety</span>
              <span className="capability"><IconBag /> Consumer fraud</span>
              <span className="capability"><IconFile /> Police &amp; FIR</span>
            </div>
          </div>
          <dl className="hero-meta">
            <div className="hero-meta-item">
              <dt>District</dt>
              <dd>
                <input
                  className="input district-input"
                  value={district}
                  onChange={(e) => setDistrict(e.target.value)}
                  placeholder="e.g. Pune"
                  aria-label="District"
                />
              </dd>
            </div>
            <div className="hero-meta-item">
              <dt>Session</dt>
              <dd>
                {sessionId ? (
                  <span className="session-chip">{sessionId.slice(0, 8)}…</span>
                ) : (
                  <span className="muted" style={{ fontFamily: "var(--font-display-stack)", fontSize: 16 }}>
                    fresh
                  </span>
                )}
              </dd>
            </div>
          </dl>
        </section>

        <section className="grid-main">
          {/* ---------- Voice panel ---------- */}
          <article className="panel" aria-labelledby="voice-heading">
            <div className="voice-stage">
              <div className="voice-status" aria-live="polite">
                <span className={`status-dot ${voiceStatusKind}`} aria-hidden="true" />
                <span>{voiceStatusLabel}</span>
              </div>

              <div className="voice-orb-wrap">
                <div className={`voice-rings ${voiceListening ? "listening" : ""}`} aria-hidden="true">
                  <span /><span /><span />
                </div>
                {voiceListening ? (
                  <button
                    type="button"
                    onClick={stopVoiceListening}
                    className="voice-orb listening"
                    aria-label="Stop listening"
                  >
                    <span className="voice-orb-icon" aria-hidden="true"><IconStop /></span>
                    <span className="voice-orb-label">Listening</span>
                    <span className="voice-orb-sub">Tap when finished</span>
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={startVoiceListening}
                    disabled={voiceWorking || canUseBrowserVoice === false}
                    className="voice-orb"
                    aria-label={voiceWorking ? "Working" : "Tap to speak"}
                  >
                    <span className="voice-orb-icon" aria-hidden="true"><IconMic /></span>
                    <span className="voice-orb-label">{voiceWorking ? "Thinking…" : "Tap to speak"}</span>
                    <span className="voice-orb-sub">
                      {voiceWorking ? "Almost there" : "Speak in any of 5 languages"}
                    </span>
                  </button>
                )}
              </div>

              <p className="voice-prompt">
                {voiceListening
                  ? "Say what happened — dates, district, who did what."
                  : voiceLastHeard
                    ? `Last heard · "${voiceLastHeard}"`
                    : "Press the button and tell us your situation in plain words."}
              </p>
            </div>

            <div className="panel-divider" />

            <div className="panel-body" id="voice-heading">
              <h2 className="panel-title" style={{ fontSize: 18, marginBottom: 6 }}>Or type it out</h2>
              <p className="panel-sub">Same advice, just from the keyboard.</p>
              <form onSubmit={runOrchestrate} style={{ marginTop: 14 }}>
                <textarea
                  className="textarea"
                  rows={5}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="e.g. My landlord changed the locks last Tuesday and is refusing to return my deposit."
                />
                <div className="btn-row">
                  <button type="submit" className="btn btn--primary" disabled={loading}>
                    {loading ? "Reading your message…" : "Get guidance"}
                  </button>
                  <button
                    type="button"
                    onClick={downloadPdf}
                    disabled={pdfLoading}
                    className="btn btn--ghost"
                  >
                    {pdfLoading ? "Generating…" : "Download complaint PDF"}
                  </button>
                </div>
              </form>
            </div>
          </article>

          {/* ---------- Guidance panel ---------- */}
          <article className="panel">
            <div className="panel-header">
              <div>
                <h2 className="panel-title">Guidance</h2>
                <p className="panel-sub">A short read, not legal advice — verify with DLSA or a lawyer.</p>
              </div>
              {orchestrateResult ? (
                <span className={`tag${orchestrateResult.crisis_detected ? " danger" : orchestrateResult.needs_clarification ? " warm" : ""}`}>
                  {orchestrateResult.crisis_detected
                    ? "Safety first"
                    : orchestrateResult.needs_clarification
                      ? "More detail helps"
                      : categoryLabel || "General"}
                </span>
              ) : null}
            </div>

            <div className="panel-divider" />

            <div className="guidance">
              {orchestrateResult ? (
                <>
                  <p className="guidance-summary">{orchestrateResult.rights_summary}</p>

                  {orchestrateResult.crisis_detected && orchestrateResult.helplines.length > 0 ? (
                    <div className="callout">
                      <span className="callout-title">Emergency helplines</span>
                      {orchestrateResult.helplines.join(" · ")}
                    </div>
                  ) : null}

                  {orchestrateResult.needs_clarification ? (
                    <>
                      <p className="subhead">A few quick questions</p>
                      <ul className="checklist warm">
                        {orchestrateResult.clarifying_questions.map((q) => (
                          <li key={q}>{q}</li>
                        ))}
                      </ul>
                    </>
                  ) : (
                    <>
                      <div className="section-grid">
                        {orchestrateResult.suggested_forum.length > 0 ? (
                          <div>
                            <p className="subhead">Where to go</p>
                            <ul className="checklist">
                              {orchestrateResult.suggested_forum.map((f) => (
                                <li key={f}>{f}</li>
                              ))}
                            </ul>
                          </div>
                        ) : null}
                        {orchestrateResult.required_documents.length > 0 ? (
                          <div>
                            <p className="subhead">Papers to gather</p>
                            <ul className="checklist">
                              {orchestrateResult.required_documents.map((d) => (
                                <li key={d}>{d}</li>
                              ))}
                            </ul>
                          </div>
                        ) : null}
                      </div>

                      {orchestrateResult.limitation_hint ? (
                        <div className="callout">
                          <span className="callout-title">About time limits</span>
                          {orchestrateResult.limitation_hint}
                        </div>
                      ) : null}

                      {orchestrateResult.free_legal_aid.length > 0 ? (
                        <div className="callout" style={{ marginTop: 10 }}>
                          <span className="callout-title">Free legal aid</span>
                          {orchestrateResult.free_legal_aid.join(" · ")}
                        </div>
                      ) : null}
                    </>
                  )}

                  <p className="disclaimer">{orchestrateResult.disclaimer}</p>
                </>
              ) : (
                <div className="guidance-empty">
                  <p style={{ margin: 0, fontSize: 14 }}>
                    Your guidance will appear here. Try saying or typing
                    <br />
                    <strong style={{ color: "var(--ink)" }}>“my employer hasn&rsquo;t paid me for two months.”</strong>
                  </p>
                </div>
              )}
            </div>
          </article>
        </section>

        {/* ---------- Conversation history ---------- */}
        <article className="panel" style={{ marginTop: 22 }}>
          <div className="panel-header">
            <div>
              <h2 className="panel-title">Conversation</h2>
              <p className="panel-sub">
                Nyaay Sathi remembers this thread on this device. Ask &ldquo;how can you help?&rdquo; anytime.
              </p>
            </div>
            <button type="button" onClick={startNewConversation} className="btn btn--quiet btn--sm">
              Start over
            </button>
          </div>

          <div className="panel-divider" />

          <div className="conversation">
            {chatHistory.length === 0 ? (
              <div className="chat-empty">
                No messages yet. Speak or type to begin — your conversation stays private to this browser.
              </div>
            ) : (
              <div className="chat-log">
                {chatHistory.map((m, i) => (
                  <div
                    key={`${m.created_at}-${i}`}
                    className={`chat-msg ${m.role === "user" ? "user" : "assistant"}`}
                  >
                    <div className="chat-avatar" aria-hidden="true">
                      {m.role === "user" ? "You" : "NS"}
                    </div>
                    <div>
                      <div className="chat-msg-bubble">{m.content}</div>
                      <div className="chat-msg-meta">
                        {m.role === "user" ? "You" : "Nyaay Sathi"}
                        {m.category && m.role === "assistant" ? ` · ${formatCategory(m.category)}` : ""}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </article>

        {error ? (
          <div className="alert" role="alert">
            <IconWarning />
            <span>{error}</span>
          </div>
        ) : null}
      </main>

      <footer className="footer">
        <span>© {new Date().getFullYear()} Nyaay Sathi · Built for everyday access to Indian law.</span>
        <span className="footer-links">
          <span>Information, not legal advice.</span>
          <span>For emergencies, call 112.</span>
        </span>
      </footer>
    </div>
  );
}

/* ----------------------------- helpers & icons ----------------------------- */

function formatCategory(c: string): string {
  switch (c) {
    case "employment_wages": return "Wages & work";
    case "property_tenancy": return "Rent & property";
    case "womens_protection": return "Women's safety";
    case "consumer_fraud": return "Consumer";
    case "police_fir": return "Police & FIR";
    case "general": return "General";
    default: return c;
  }
}

const ICON_PROPS = {
  width: 16,
  height: 16,
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.6,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
};

function IconBriefcase() {
  return (
    <svg {...ICON_PROPS}>
      <rect x="3" y="7" width="18" height="13" rx="2" />
      <path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2" />
      <path d="M3 13h18" />
    </svg>
  );
}
function IconHome() {
  return (
    <svg {...ICON_PROPS}>
      <path d="M3 11l9-7 9 7" />
      <path d="M5 10v9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-9" />
    </svg>
  );
}
function IconShield() {
  return (
    <svg {...ICON_PROPS}>
      <path d="M12 3l8 3v6c0 5-3.5 8.5-8 9-4.5-.5-8-4-8-9V6l8-3z" />
    </svg>
  );
}
function IconBag() {
  return (
    <svg {...ICON_PROPS}>
      <path d="M5 8h14l-1 12H6L5 8z" />
      <path d="M9 8a3 3 0 0 1 6 0" />
    </svg>
  );
}
function IconFile() {
  return (
    <svg {...ICON_PROPS}>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" />
      <path d="M14 3v5h5" />
    </svg>
  );
}
function IconMic() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="3" width="6" height="11" rx="3" />
      <path d="M5 11a7 7 0 0 0 14 0" />
      <path d="M12 18v3" />
      <path d="M9 21h6" />
    </svg>
  );
}
function IconStop() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
      <rect x="6" y="6" width="12" height="12" rx="2" />
    </svg>
  );
}
function IconWarning() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3l10 18H2L12 3z" />
      <path d="M12 10v5" />
      <circle cx="12" cy="18" r="0.8" fill="currentColor" />
    </svg>
  );
}
