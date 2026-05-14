import gradio as gr
from main import main   # returns {"match_score": float, "categories": {...}}


# ── HTML builders ─────────────────────────────────────────────────────────────

CATEGORY_ICONS = {
    "Web Development":       "🌐",
    "Programming Languages": "💻",
    "Data Science & ML":     "🤖",
    "Data Engineering":      "🔧",
    "Cloud & DevOps":        "☁️",
    "Databases":             "🗄️",
    "Control & Automation":  "⚙️",
    "Algorithms & CS":       "📐",
    "Version Control & PM":  "🔀",
    "Security":              "🔒",
    "Soft Skills":           "🤝",
    "Other":                 "📌",
}

def chip(text: str, color: str) -> str:
    return (
        f"<span style='"
        f"display:inline-block;margin:3px 3px;padding:3px 11px;"
        f"background:{color}1a;color:{color};border:1px solid {color}44;"
        f"border-radius:999px;font-size:12px;font-family:monospace;"
        f"white-space:nowrap"
        f"'>{text}</span>"
    )

def category_card(name: str, matched: list, missing: list) -> str:
    icon   = CATEGORY_ICONS.get(name, "📌")
    total  = len(matched) + len(missing)
    pct    = int(len(matched) / total * 100) if total else 0
    bar_color = "#22c55e" if pct >= 70 else "#f59e0b" if pct >= 40 else "#ef4444"

    matched_chips = "".join(chip(k, "#22c55e") for k in matched) if matched else ""
    missing_chips = "".join(chip(k, "#ef4444") for k in missing) if missing else ""

    all_chips = matched_chips + missing_chips

    return f"""
    <div style='background:#1e293b;border:1px solid #334155;border-radius:10px;
                padding:14px 16px;margin-bottom:12px'>
        <div style='display:flex;align-items:center;justify-content:space-between;margin-bottom:8px'>
            <span style='font-size:14px;font-weight:700;color:#e2e8f0'>
                {icon}&nbsp; {name}
            </span>
            <span style='font-size:12px;color:#64748b'>
                {len(matched)}/{total} matched
            </span>
        </div>
        <!-- progress bar -->
        <div style='height:4px;background:#0f172a;border-radius:2px;margin-bottom:10px'>
            <div style='height:4px;width:{pct}%;background:{bar_color};
                        border-radius:2px;transition:width .4s'></div>
        </div>
        <div style='line-height:2'>{all_chips}</div>
    </div>
    """

def score_html(score: float) -> str:
    color = "#22c55e" if score >= 70 else "#f59e0b" if score >= 40 else "#ef4444"
    label = "Strong Match" if score >= 70 else "Partial Match" if score >= 40 else "Weak Match"
    tips = {
        "Strong Match":  "Great fit — tailor the summary section and apply.",
        "Partial Match": "Add the missing skills or highlight adjacent experience.",
        "Weak Match":    "Consider upskilling in the missing categories first.",
    }
    return f"""
    <div style='text-align:center;padding:28px 16px;
                background:#1e293b;border:1px solid #334155;border-radius:12px'>
        <div style='font-size:72px;font-weight:900;color:{color};
                    font-family:monospace;letter-spacing:-3px;line-height:1'>
            {score}<span style='font-size:32px'>%</span>
        </div>
        <div style='margin-top:10px;font-size:15px;font-weight:700;
                    color:{color};letter-spacing:1.5px;text-transform:uppercase'>
            {label}
        </div>
        <div style='margin-top:8px;font-size:13px;color:#64748b;max-width:260px;margin-inline:auto'>
            {tips[label]}
        </div>
    </div>
    """


# ── Handler ───────────────────────────────────────────────────────────────────

def run_analysis(pdf_file, jd_text: str):
    if pdf_file is None:
        raise gr.Error("Please upload a resume PDF.")
    if not jd_text.strip():
        raise gr.Error("Please paste a job description.")

    result     = main(pdf_file.name, jd_text)
    score      = float(str(result["match_score"]).replace("%", ""))
    categories = result.get("categories", {})

    # Sort: categories with most keywords first
    sorted_cats = sorted(
        categories.items(),
        key=lambda kv: len(kv[1]["matched"]) + len(kv[1]["missing"]),
        reverse=True,
    )

    cards_html = "".join(
        category_card(name, data["matched"], data["missing"])
        for name, data in sorted_cats
        if data["matched"] or data["missing"]
    )

    return score_html(score), cards_html or "<p style='color:#475569'>No skill categories detected.</p>"


# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
body, .gradio-container { background:#0f172a !important; }

textarea {
    background:#0f172a !important; color:#e2e8f0 !important;
    border:1px solid #334155 !important; border-radius:8px !important;
    font-size:14px !important;
}
textarea:focus { border-color:#6366f1 !important; box-shadow:0 0 0 3px #6366f133 !important; }

[data-testid="file-upload"], .upload-container {
    background:#0f172a !important;
    border:2px dashed #334155 !important;
    border-radius:8px !important;
}
[data-testid="file-upload"]:hover { border-color:#6366f1 !important; }

#run-btn {
    background:linear-gradient(135deg,#6366f1,#818cf8) !important;
    color:#fff !important; font-weight:700 !important; font-size:15px !important;
    border-radius:8px !important; border:none !important;
    padding:12px 0 !important; transition:opacity .2s !important;
}
#run-btn:hover { opacity:.85 !important; }

.section-label {
    font-size:11px; font-weight:700; letter-spacing:2px;
    text-transform:uppercase; color:#64748b; margin-bottom:6px;
}

#skills-scroll { max-height:520px; overflow-y:auto;
    scrollbar-width:thin; scrollbar-color:#334155 transparent; }
"""


# ── Layout ────────────────────────────────────────────────────────────────────

with gr.Blocks(css=CSS, title="Resume Matcher") as demo:

    gr.HTML("""
        <div style='padding:32px 0 20px;text-align:center'>
            <div style='font-size:26px;font-weight:800;color:#e2e8f0;letter-spacing:-.5px'>
                Resume <span style='color:#818cf8'>Matcher</span>
            </div>
            <div style='color:#64748b;font-size:13px;margin-top:5px'>
                Upload a résumé PDF · paste a job description · see skill gaps instantly
            </div>
        </div>
    """)

    with gr.Row(equal_height=False):

        # Left — inputs
        with gr.Column(scale=4):
            gr.HTML("<div class='section-label'>Resume PDF</div>")
            pdf_in = gr.File(label="", file_types=[".pdf"], height=110)

            gr.HTML("<div class='section-label' style='margin-top:14px'>Job Description</div>")
            jd_in = gr.Textbox(label="", placeholder="Paste the full job description…",
                               lines=15, max_lines=22)

            run_btn = gr.Button("Analyse →", elem_id="run-btn")

        # Right — outputs
        with gr.Column(scale=6):
            gr.HTML("<div class='section-label'>Match Score</div>")
            score_out = gr.HTML(
                "<div style='text-align:center;padding:28px;color:#475569;font-size:13px'>"
                "Results will appear here after analysis.</div>"
            )

            gr.HTML("<div class='section-label' style='margin-top:18px'>Skill Breakdown</div>")
            skills_out = gr.HTML(
                "<p style='color:#475569;font-size:13px'>—</p>",
                elem_id="skills-scroll",
            )

    run_btn.click(
        fn=run_analysis,
        inputs=[pdf_in, jd_in],
        outputs=[score_out, skills_out],
    )

if __name__ == "__main__":
    demo.launch()