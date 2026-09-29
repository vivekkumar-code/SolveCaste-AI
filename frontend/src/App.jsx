import { useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [activePage, setActivePage] = useState("new");
  const [activeTab, setActiveTab] = useState("solution");

  const [question, setQuestion] = useState("");
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);

  const [solution, setSolution] = useState(null);
  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  const [doubt, setDoubt] = useState("");
  const [doubtAnswer, setDoubtAnswer] = useState("");
  const [doubtLoading, setDoubtLoading] = useState(false);

  const [history, setHistory] = useState([]);

  const [profileName, setProfileName] = useState(
    () => localStorage.getItem("solvecast_profile_name") || "User"
  );

  const [profileOpen, setProfileOpen] = useState(false);
  const [editName, setEditName] = useState("");

  const [showNotes, setShowNotes] = useState(false);
  const [showSaved, setShowSaved] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const fileInputRef = useRef(null);

  // =====================================================
  // LOAD HISTORY
  // =====================================================

  useEffect(() => {
    const saved = localStorage.getItem("solvecast_history");

    if (saved) {
      try {
        setHistory(JSON.parse(saved));
      } catch {
        setHistory([]);
      }
    }
  }, []);

  // =====================================================
  // IMAGE
  // =====================================================

  const handleImageChange = (e) => {
    const file = e.target.files?.[0];

    if (!file) return;

    setImage(file);
    setPreview(URL.createObjectURL(file));
    setError("");
  };

  const removeImage = () => {
    setImage(null);
    setPreview(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // =====================================================
  // HISTORY
  // =====================================================

  const saveHistory = (result) => {
    const item = {
      id: Date.now(),
      question: result.question || question || "Untitled question",
      solution: result,
      date: new Date().toLocaleString(),
    };

    const updated = [
      item,
      ...history.filter(
        (x) => x.question !== item.question
      ),
    ].slice(0, 30);

    setHistory(updated);

    localStorage.setItem(
      "solvecast_history",
      JSON.stringify(updated)
    );
  };

  // =====================================================
  // EXTRACT BACKEND RESPONSE
  // =====================================================

  const extractSolution = (data) => {
    if (!data) {
      throw new Error("Empty response from backend.");
    }

    if (data.success === false) {
      throw new Error(
        data.error || "Backend failed."
      );
    }

    const result = data.solution ?? data;

    if (!result) {
      throw new Error("Solution not found.");
    }

    return result;
  };

  // =====================================================
  // SOLVE
  // =====================================================

  const handleSolve = async () => {
    if (!image && !question.trim()) {
      setError(
        "Please enter a question or upload an image."
      );
      return;
    }

    setLoading(true);
    setError("");
    setSolution(null);
    setDoubt("");
    setDoubtAnswer("");

    try {
      let response;

      if (image) {
        const formData = new FormData();

        formData.append("file", image);

        response = await fetch(
          `${API_URL}/solve-image`,
          {
            method: "POST",
            body: formData,
          }
        );
      } else {
        const formData = new FormData();

        formData.append(
          "question",
          question.trim()
        );

        response = await fetch(
          `${API_URL}/solve`,
          {
            method: "POST",
            body: formData,
          }
        );
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Server error."
        );
      }

      const result = extractSolution(data);

      setSolution(result);
      setActivePage("new");
      setActiveTab("solution");

      saveHistory(result);
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // DOUBT
  // =====================================================

  const askDoubt = async () => {
    if (!doubt.trim() || !solution) {
      return;
    }

    setDoubtLoading(true);
    setDoubtAnswer("");
    setError("");

    try {
      const solutionText = [
        ...(solution.steps || []),
        solution.final_answer
          ? `Final Answer: ${solution.final_answer}`
          : "",
      ]
        .filter(Boolean)
        .join("\n");

      const response = await fetch(
        `${API_URL}/doubt`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            question:
              solution.question ||
              question,
            solution: solutionText,
            doubt: doubt.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok || data.success === false) {
        throw new Error(
          data.error ||
            "Unable to answer doubt."
        );
      }

      setDoubtAnswer(
        data.answer ||
          "No answer received."
      );
    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Something went wrong."
      );
    } finally {
      setDoubtLoading(false);
    }
  };

  // =====================================================
  // OPEN DOUBT SYSTEM
  // =====================================================

  const openDoubtSystem = () => {
    if (!solution) {
      setError(
        "Please solve a question first."
      );
      setActivePage("new");
      return;
    }

    setError("");
    setActivePage("new");
    setActiveTab("doubt");

    setTimeout(() => {
      document
        .getElementById("doubt-box")
        ?.focus();
    }, 100);
  };

  // =====================================================
  // HISTORY OPEN
  // =====================================================

  const openHistory = (item) => {
    setSolution(item.solution);

    setQuestion(
      item.solution.question || ""
    );

    setImage(null);
    setPreview(null);

    setActivePage("new");
    setActiveTab("solution");

    setError("");
    setDoubt("");
    setDoubtAnswer("");
  };

  // =====================================================
  // NEW QUESTION
  // =====================================================

  const newQuestion = () => {
    setActivePage("new");

    setQuestion("");
    setImage(null);
    setPreview(null);
    setSolution(null);

    setError("");
    setDoubt("");
    setDoubtAnswer("");

    setActiveTab("solution");

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // =====================================================
  // SUBJECT
  // =====================================================

  const getSubject = () => {
    const text = (
      solution?.question ||
      question ||
      ""
    ).toLowerCase();

    if (
      text.includes("physics") ||
      text.includes("force") ||
      text.includes("mass") ||
      text.includes("velocity") ||
      text.includes("acceleration") ||
      text.includes("friction") ||
      text.includes("motion") ||
      text.includes("momentum") ||
      text.includes("projectile")
    ) {
      return "Physics";
    }

    if (
      text.includes("chemistry") ||
      text.includes("atom") ||
      text.includes("molecule") ||
      text.includes("reaction") ||
      text.includes("equilibrium")
    ) {
      return "Chemistry";
    }

    if (
      text.includes("biology") ||
      text.includes("cell") ||
      text.includes("dna") ||
      text.includes("neuron")
    ) {
      return "Biology";
    }

    if (
      text.includes("code") ||
      text.includes("algorithm") ||
      text.includes("program") ||
      text.includes("tree") ||
      text.includes("graph") ||
      text.includes("sql") ||
      text.includes("database")
    ) {
      return "Computer Science";
    }

    return "Mathematics";
  };

  // =====================================================
  // RELATED QUESTIONS
  // =====================================================

  const relatedQuestions = [
    "A block on an inclined plane with friction",
    "Find the acceleration when μ = 0",
    "Motion on a rough inclined plane",
    "Derive formula for normal reaction",
  ];

  // =====================================================
  // PROFILE
  // =====================================================

  const saveProfileName = () => {
    const name =
      editName.trim() || "User";

    setProfileName(name);

    localStorage.setItem(
      "solvecast_profile_name",
      name
    );

    setProfileOpen(false);
  };

  // =====================================================
  // DOWNLOAD SVG
  // =====================================================

  const downloadSVG = () => {
    if (!solution?.diagram_svg) {
      setError(
        "No diagram available to download."
      );
      return;
    }

    const blob = new Blob(
      [solution.diagram_svg],
      {
        type: "image/svg+xml",
      }
    );

    const url =
      URL.createObjectURL(blob);

    const a =
      document.createElement("a");

    a.href = url;
    a.download =
      "solvecast-diagram.svg";

    document.body.appendChild(a);
    a.click();

    document.body.removeChild(a);

    URL.revokeObjectURL(url);
  };

  // =====================================================
  // EXPLAIN CONCEPT
  // =====================================================

  const explainConcept = () => {
    if (!solution) {
      setError(
        "Please solve a question first."
      );
      return;
    }

    setActiveTab("concepts");
  };

  // =====================================================
  // RELATED QUESTION
  // =====================================================

  const useRelatedQuestion = (text) => {
    setQuestion(text);
    setImage(null);
    setPreview(null);
    setSolution(null);
    setError("");
    setDoubtAnswer("");

    setActivePage("new");
    setActiveTab("solution");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // =====================================================
  // RENDER
  // =====================================================

  return (
    <div className="dashboard">

      {/* =================================================
          SIDEBAR
      ================================================= */}

      <aside className="sidebar">

        <div className="logo-area">

          <div className="logo-mark">
            🎓
          </div>

          <div>
            <h1>SolveCast AI</h1>
            <p>
              Your Personal AI Tutor
            </p>
          </div>

        </div>

        <button
          className="new-question-btn"
          onClick={newQuestion}
        >
          <span>⊞</span>
          New Question
        </button>

        <nav className="sidebar-nav">

          {/* HISTORY */}

          <button
            className={
              activePage === "history"
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => {
              setActivePage("history");
              setError("");
            }}
          >
            <span>▣</span>
            Browse History
          </button>

          {/* NOTES */}

          <button
            className={
              showNotes
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => {
              setShowNotes(!showNotes);
              setShowSaved(false);
              setShowSettings(false);
              setError("");
            }}
          >
            <span>▤</span>
            Notes & PDFs
          </button>

          {/* DOUBT */}

          <button
            className="nav-item"
            onClick={openDoubtSystem}
          >
            <span>?</span>
            Doubt System
          </button>

          {/* SAVED */}

          <button
            className={
              showSaved
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => {
              setShowSaved(!showSaved);
              setShowNotes(false);
              setShowSettings(false);
              setError("");
            }}
          >
            <span>♡</span>
            Saved Solutions
          </button>

          {/* SETTINGS */}

          <button
            className={
              showSettings
                ? "nav-item active"
                : "nav-item"
            }
            onClick={() => {
              setShowSettings(
                !showSettings
              );

              setShowNotes(false);
              setShowSaved(false);
              setError("");
            }}
          >
            <span>⚙</span>
            Settings
          </button>

        </nav>

        <div className="sidebar-promo">

          <div className="promo-bot">
            ✦
          </div>

          <h3>
            Solve Anything
          </h3>

          <h3>
            Learn Better
          </h3>

          <h3>
            With AI ✨
          </h3>

        </div>

      </aside>

      {/* =================================================
          MAIN AREA
      ================================================= */}

      <main className="main-area">

        {/* TOP BAR */}

        <header className="dashboard-header">

          <div></div>

          <div className="header-actions">

            <button className="theme-btn">
              ☼
            </button>

            <div className="profile-wrapper">

              <button
                className="profile"
                onClick={() => {
                  setEditName(
                    profileName
                  );

                  setProfileOpen(
                    !profileOpen
                  );
                }}
              >

                <div className="profile-avatar">
                  {profileName
                    .charAt(0)
                    .toUpperCase()}
                </div>

                <span>
                  {profileName}
                </span>

                <span>
                  ⌄
                </span>

              </button>

              {profileOpen && (
                <div className="profile-menu">

                  <div className="profile-menu-title">
                    Profile
                  </div>

                  <input
                    type="text"
                    value={editName}
                    onChange={(e) =>
                      setEditName(
                        e.target.value
                      )
                    }
                    placeholder="Enter your name"
                    maxLength={30}
                    autoFocus
                  />

                  <button
                    className="save-profile-btn"
                    onClick={
                      saveProfileName
                    }
                  >
                    Save
                  </button>

                </div>
              )}

            </div>

          </div>

        </header>

        {/* =================================================
            SIMPLE PANELS
        ================================================= */}

        {showNotes ? (

          <section className="simple-page">

            <h2>
              Notes & PDFs
            </h2>

            <p className="page-subtitle">
              Your study notes and PDF
              workspace.
            </p>

            <div className="feature-card">

              <div className="feature-icon">
                📚
              </div>

              <h3>
                Notes & PDF System
              </h3>

              <p>
                RAG based notes and PDF
                support will be added
                in Phase 2.
              </p>

            </div>

          </section>

        ) : showSaved ? (

          <section className="simple-page">

            <h2>
              Saved Solutions
            </h2>

            <p className="page-subtitle">
              Your solved questions
              are stored in browser
              history.
            </p>

            {history.length === 0 ? (

              <div className="empty-state">

                <div>♡</div>

                <h3>
                  No saved solutions
                </h3>

                <p>
                  Solve a question first.
                </p>

              </div>

            ) : (

              <div className="history-grid">

                {history.map(
                  (item) => (

                    <button
                      className="history-card"
                      key={item.id}
                      onClick={() =>
                        openHistory(item)
                      }
                    >

                      <div className="history-card-icon">
                        ✓
                      </div>

                      <div>

                        <h3>
                          {item.question}
                        </h3>

                        <p>
                          {item.date}
                        </p>

                      </div>

                    </button>

                  )
                )}

              </div>

            )}

          </section>

        ) : showSettings ? (

          <section className="simple-page">

            <h2>
              Settings
            </h2>

            <p className="page-subtitle">
              Manage your SolveCast AI
              preferences.
            </p>

            <div className="feature-card">

              <div className="feature-icon">
                ⚙
              </div>

              <h3>
                Local Settings
              </h3>

              <p>
                Your profile name and
                question history are
                currently stored locally
                in your browser.
              </p>

              <button
                className="clear-history-btn"
                onClick={() => {

                  localStorage.removeItem(
                    "solvecast_history"
                  );

                  setHistory([]);

                  setError(
                    "History cleared successfully."
                  );

                }}
              >
                Clear History
              </button>

            </div>

          </section>

        ) : activePage === "history" ? (

          /* =================================================
             HISTORY PAGE
          ================================================= */

          <section className="history-page">

            <h2>
              Browse History
            </h2>

            <p className="page-subtitle">
              Your previously solved
              questions
            </p>

            {history.length === 0 ? (

              <div className="empty-state">

                <div>◴</div>

                <h3>
                  No solved questions yet
                </h3>

                <p>
                  Your solved questions
                  will appear here.
                </p>

              </div>

            ) : (

              <div className="history-grid">

                {history.map(
                  (item) => (

                    <button
                      className="history-card"
                      key={item.id}
                      onClick={() =>
                        openHistory(item)
                      }
                    >

                      <div className="history-card-icon">
                        ✓
                      </div>

                      <div>

                        <h3>
                          {item.question}
                        </h3>

                        <p>
                          {item.date}
                        </p>

                      </div>

                    </button>

                  )
                )}

              </div>

            )}

          </section>

        ) : (

          <>
            {/* =================================================
                QUESTION CARD
            ================================================= */}

            <section className="question-card">

              <div className="question-top">

                <span className="subject-badge">
                  ⚯ {getSubject()}
                </span>

                <p className="question-text">
                  {question ||
                    "Enter your question to start learning with SolveCast AI."}
                </p>

              </div>

              <div className="question-actions">

                <button
                  className="input-action"
                  onClick={() =>
                    fileInputRef.current?.click()
                  }
                >
                  ◉ Upload Image
                </button>

                <button
                  className="input-action selected"
                  onClick={() =>
                    document
                      .getElementById(
                        "question-input"
                      )
                      ?.focus()
                  }
                >
                  ☷ Text Question
                </button>

                <button
                  className="input-action"
                  onClick={() =>
                    setError(
                      "Camera capture will be added later."
                    )
                  }
                >
                  ◉ Capture
                </button>

                <button
                  className="solve-main-btn"
                  onClick={handleSolve}
                  disabled={loading}
                >
                  {loading
                    ? "Solving..."
                    : "Solve  →"}
                </button>

              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept="image/png,image/jpeg,image/jpg"
                onChange={
                  handleImageChange
                }
                hidden
              />

              {preview && (

                <div className="uploaded-preview">

                  <img
                    src={preview}
                    alt="Question"
                  />

                  <button
                    onClick={removeImage}
                  >
                    ×
                  </button>

                </div>

              )}

              <textarea
                id="question-input"
                className="main-question-input"
                value={question}
                onChange={(e) =>
                  setQuestion(
                    e.target.value
                  )
                }
                placeholder="Type your question here..."
              />

            </section>

            {/* ERROR */}

            {error && (

              <div className="error-banner">
                {error}
              </div>

            )}

            {/* =================================================
                TABS
            ================================================= */}

            {solution && (

              <div className="content-tabs">

                <button
                  className={
                    activeTab === "solution"
                      ? "content-tab active"
                      : "content-tab"
                  }
                  onClick={() =>
                    setActiveTab(
                      "solution"
                    )
                  }
                >
                  ▣ Solution
                </button>

                <button
                  className={
                    activeTab === "diagram"
                      ? "content-tab active"
                      : "content-tab"
                  }
                  onClick={() =>
                    setActiveTab(
                      "diagram"
                    )
                  }
                >
                  ◇ Diagram
                </button>

                <button
                  className={
                    activeTab === "concepts"
                      ? "content-tab active"
                      : "content-tab"
                  }
                  onClick={() =>
                    setActiveTab(
                      "concepts"
                    )
                  }
                >
                  ♧ Key Concepts
                </button>

                <button
                  className={
                    activeTab === "doubt"
                      ? "content-tab active"
                      : "content-tab"
                  }
                  onClick={() =>
                    setActiveTab(
                      "doubt"
                    )
                  }
                >
                  ♧ Doubt (Ask AI)
                </button>

              </div>

            )}

            {/* =================================================
                CONTENT
            ================================================= */}

            {solution && (

              <div className="workspace">

                {/* LEFT CONTENT */}

                <section className="solution-column">

                  {/* SOLUTION */}

                  {activeTab ===
                    "solution" && (

                    <div className="panel">

                      <div className="panel-title">

                        <span>☷</span>

                        <h2>
                          Step-by-Step
                          Solution
                        </h2>

                      </div>

                      <div className="steps-list">

                        {(solution.steps ||
                          []
                        ).map(
                          (
                            step,
                            index
                          ) => (

                            <div
                              className="solution-step"
                              key={index}
                            >

                              <div className="step-badge">
                                {index +
                                  1}
                              </div>

                              <div className="step-body">
                                {step}
                              </div>

                            </div>

                          )
                        )}

                      </div>

                      {solution.final_answer && (

                        <div className="final-box">

                          <div className="final-icon">
                            ✓
                          </div>

                          <div>

                            <span>
                              Final Answer
                            </span>

                            <p>
                              {
                                solution.final_answer
                              }
                            </p>

                          </div>

                        </div>

                      )}

                    </div>

                  )}

                  {/* DIAGRAM */}

                  {activeTab ===
                    "diagram" && (

                    <div className="panel">

                      <div className="panel-title">

                        <span>◇</span>

                        <h2>
                          Generated
                          Diagram
                        </h2>

                      </div>

                      {solution.diagram_svg ? (

                        <div
                          className="large-diagram"
                          dangerouslySetInnerHTML={{
                            __html:
                              solution.diagram_svg,
                          }}
                        />

                      ) : (

                        <div className="no-diagram">
                          No diagram is
                          required for this
                          question.
                        </div>

                      )}

                    </div>

                  )}

                  {/* CONCEPTS */}

                  {activeTab ===
                    "concepts" && (

                    <div className="panel">

                      <div className="panel-title">

                        <span>♧</span>

                        <h2>
                          Key Concepts
                        </h2>

                      </div>

                      <div className="concept-list">

                        <div className="concept">
                          <b>1.</b>
                          Understand the
                          given values.
                        </div>

                        <div className="concept">
                          <b>2.</b>
                          Identify the
                          required formula.
                        </div>

                        <div className="concept">
                          <b>3.</b>
                          Substitute the
                          values.
                        </div>

                        <div className="concept">
                          <b>4.</b>
                          Verify the final
                          result.
                        </div>

                      </div>

                    </div>

                  )}

                  {/* DOUBT */}

                  {activeTab ===
                    "doubt" && (

                    <div className="panel">

                      <div className="panel-title">

                        <span>♧</span>

                        <h2>
                          Ask AI About
                          This Solution
                        </h2>

                      </div>

                      <textarea
                        id="doubt-box"
                        className="doubt-textarea"
                        value={doubt}
                        onChange={(e) =>
                          setDoubt(
                            e.target.value
                          )
                        }
                        placeholder="Ask anything about this solution..."
                      />

                      <button
                        className="ask-btn"
                        onClick={
                          askDoubt
                        }
                        disabled={
                          doubtLoading ||
                          !doubt.trim()
                        }
                      >
                        {doubtLoading
                          ? "Thinking..."
                          : "Ask AI →"}
                      </button>

                      {doubtAnswer && (

                        <div className="ai-answer">

                          <b>
                            AI Answer
                          </b>

                          <p>
                            {
                              doubtAnswer
                            }
                          </p>

                        </div>

                      )}

                    </div>

                  )}

                </section>

                {/* RIGHT WORKSPACE */}

                <aside className="right-workspace">

                  {/* DIAGRAM */}

                  <div className="side-panel">

                    <div className="side-title">

                      <div>

                        <span>◇</span>

                        <h3>
                          Diagram
                        </h3>

                      </div>

                      <button
                        onClick={
                          downloadSVG
                        }
                      >
                        ↓ Download SVG
                      </button>

                    </div>

                    {solution.diagram_svg ? (

                      <div
                        className="diagram-preview"
                        dangerouslySetInnerHTML={{
                          __html:
                            solution.diagram_svg,
                        }}
                      />

                    ) : (

                      <div className="diagram-empty">
                        No diagram required.
                      </div>

                    )}

                  </div>

                  {/* KEY FORMULAS */}

                  <div className="side-panel">

                    <div className="side-title simple">

                      <div>

                        <span>∑</span>

                        <h3>
                          Key Formulas
                          Used
                        </h3>

                      </div>

                    </div>

                    <ul className="formula-list">

                      <li>
                        N = mg cos θ
                      </li>

                      <li>
                        f = μN
                      </li>

                      <li>
                        F = mg sin θ − f
                      </li>

                      <li>
                        a = F / m
                      </li>

                    </ul>

                  </div>

                </aside>

                {/* FAR RIGHT SIDEBAR */}

                <aside className="tools-sidebar">

                  <div className="tools-panel">

                    <h3>
                      ◈ Related Tools
                    </h3>

                    <button
                      className="tool-card"
                      onClick={
                        explainConcept
                      }
                    >

                      <span>▣</span>

                      <div>

                        <b>
                          Explain Concept
                        </b>

                        <small>
                          Get a simple
                          explanation
                        </small>

                      </div>

                    </button>

                    <button
                      className="tool-card"
                      onClick={() =>
                        setActiveTab(
                          "doubt"
                        )
                      }
                    >

                      <span>?</span>

                      <div>

                        <b>
                          Ask Doubt
                        </b>

                        <small>
                          Ask AI about
                          this solution
                        </small>

                      </div>

                    </button>

                    <button
                      className="tool-card"
                      onClick={() =>
                        setError(
                          "Notes & PDF system will be added in Phase 2."
                        )
                      }
                    >

                      <span>▥</span>

                      <div>

                        <b>
                          Generate Notes
                        </b>

                        <small>
                          Save as study
                          notes
                        </small>

                      </div>

                    </button>

                    <button
                      className="tool-card"
                      onClick={() =>
                        setError(
                          "PDF export will be added soon."
                        )
                      }
                    >

                      <span>▣</span>

                      <div>

                        <b>
                          Convert to PDF
                        </b>

                        <small>
                          Download solution
                          as PDF
                        </small>

                      </div>

                    </button>

                  </div>

                  {/* RELATED QUESTIONS */}

                  <div className="tools-panel">

                    <div className="related-header">

                      <h3>
                        Related Questions
                      </h3>

                      <span>
                        View All
                      </span>

                    </div>

                    {relatedQuestions.map(
                      (
                        item,
                        index
                      ) => (

                        <button
                          className="related-item"
                          key={index}
                          onClick={() =>
                            useRelatedQuestion(
                              item
                            )
                          }
                        >

                          <span>
                            {index + 1}
                          </span>

                          <p>
                            {item}
                          </p>

                        </button>

                      )
                    )}

                  </div>

                  {/* DOUBT */}

                  <div className="tools-panel doubt-panel">

                    <h3>
                      ♧ Doubt? Ask AI
                    </h3>

                    <textarea
                      value={doubt}
                      onChange={(e) =>
                        setDoubt(
                          e.target.value
                        )
                      }
                      placeholder="Ask anything about this solution..."
                    />

                    <button
                      onClick={() => {

                        if (!solution) {
                          setError(
                            "Please solve a question first."
                          );
                          return;
                        }

                        setActiveTab(
                          "doubt"
                        );

                        askDoubt();

                      }}
                      disabled={
                        doubtLoading ||
                        !doubt.trim()
                      }
                    >
                      {doubtLoading
                        ? "..."
                        : "➤"}
                    </button>

                  </div>

                </aside>

              </div>

            )}

          </>

        )}

      </main>

    </div>
  );
}

export default App;