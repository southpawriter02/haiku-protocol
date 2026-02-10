# v0.3.1a — Page Configuration & Layout Foundation

<aside>

**Version:** v0.3.1a

**Parent:** v0.3.1 — Streamlit UI Development

**Status:** ⬜ Not Started

**Duration:** 15–20 minutes

**Deliverable:** Page configuration, CSS theming, header/footer, and sidebar layout scaffolding in `src/app.py`

</aside>

---

## Objective

Establish the foundational page structure and visual identity of the Streamlit application. This sub-part creates the page configuration (title, icon, layout mode), injects custom CSS for minimal theming (header, tagline, metric cards), renders the header and footer with styled HTML, and constructs the sidebar with settings (model selector, "Show raw CNL" toggle), About section, and project links. The goal is to have a professional, branded shell ready for the input/processing/output sections that follow.

---

## User Stories

**Story 1: First-Time Visitor Recognizes the Project**

> As a hiring manager visiting the live demo for the first time, I want to immediately see a professional header with the project name and a clear tagline so that I understand what the Haiku Protocol is within 5 seconds of page load.

**Story 2: User Explores Configuration Options**

> As a technical user, I want to see a sidebar with a model selector dropdown and a "Show raw CNL" checkbox so that I can understand the UI offers configurability (even if some options are scaffolding) and feel like I'm using a polished, feature-rich tool.

---

## Implementation Design

This section covers the exact Python code and CSS that establishes page config, theming, header, footer, and sidebar. The code is organized sequentially as it will appear in `src/app.py` (top to bottom).

### 1. Imports and Initial Setup

```python
"""
src/app.py - Haiku Protocol Streamlit Web Demo
===============================================

An interactive web interface for the Haiku Protocol compression pipeline.
Provides real-time document compression, metrics visualization, and
compression quality feedback via a user-friendly Streamlit UI.

This is a single-file application with no separate modules or components.
All logic is contained herein, with imports from src/encoder.py and src/validator.py.

Usage:
    streamlit run src/app.py

Environment:
    Requires OPENAI_API_KEY in .env file for live LLM-powered encoding.
"""

import streamlit as st
from typing import Dict, Any, Optional
import logging

# Configure logging (optional — Streamlit has its own output paradigm)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the encoder pipeline from Phase 2
from src.encoder import encode  # Function that returns compression dict
from src.validator import CompressionValidator  # For metrics computation

# Optional: import config if needed for API key management
# from src.config import load_config
```

### 2. Page Configuration

```python
# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
# Set page title (appears in browser tab), icon (favicon), and layout mode.
# 'wide' mode uses full viewport width instead of narrow centered column.

st.set_page_config(
    page_title="The Haiku Protocol",
    page_icon="📦",
    layout="wide",
    # Optional: initial_sidebar_state="expanded"  # Default sidebar state
)
```

**Explanation:**
- `page_title`: Browser tab title. Clear, branded, and memorable.
- `page_icon`: Favicon shown in browser tab. Emoji "📦" represents compression/packaging.
- `layout="wide"`: Full-width layout allows the side-by-side results comparison to breathe.

### 3. Custom CSS Injection

```python
# ============================================================================
# CUSTOM CSS THEMING
# ============================================================================
# Inject minimal CSS styling for header, tagline, and metric cards.
# This is lightweight theming — not a full design system. Streamlit's
# built-in components handle most styling.
#
# Classes defined here:
#   .main-header — Large, bold project title
#   .tagline — Smaller, muted subtitle
#   .metric-card — Background color for custom metric sections

st.markdown("""
<style>
    /* Main page header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f1f1f;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }

    /* Tagline / subtitle */
    .tagline {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
        font-weight: 400;
        line-height: 1.5;
    }

    /* Metric card backgrounds */
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }

    /* Optional: Override default Streamlit button styling */
    .stButton > button {
        font-weight: 600;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# NOTE: unsafe_allow_html=True is required to render custom HTML/CSS.
# This is safe here because we control all HTML content in this file.
# Dynamic user input (from the text area) is rendered in st.code() or
# st.text_area(disabled=True), which automatically escapes HTML.
```

**Explanation:**
- CSS is injected once at app startup and applies to the entire page.
- Classes are minimal: only three custom classes (header, tagline, metric-card).
- Streamlit's default styling is preserved for buttons, text areas, etc.
- Font sizes and colors are chosen for readability and professional appearance.

### 4. Header Rendering

```python
# ============================================================================
# PAGE HEADER
# ============================================================================
# Render the main title and tagline using custom CSS classes.
# These are styled HTML strings, not plain text, so they respect the CSS.

st.markdown(
    '<p class="main-header">📦 The Haiku Protocol</p>',
    unsafe_allow_html=True
)
st.markdown(
    '<p class="tagline">Lossless Semantic Compression for LLM Context Windows</p>',
    unsafe_allow_html=True
)

# Optional: Add a horizontal divider for visual separation
st.divider()
```

**Explanation:**
- Header is a styled HTML string (uses `<p>` tag and `main-header` CSS class).
- Emoji (📦) is included in the HTML string for visual branding.
- Tagline explains the project's purpose in one clear sentence.
- `st.divider()` adds a horizontal line for visual separation.

### 5. Sidebar Setup

```python
# ============================================================================
# SIDEBAR: SETTINGS & ABOUT
# ============================================================================
# The sidebar contains configuration options, documentation links, and
# project information.

with st.sidebar:
    # Section header
    st.header("⚙️ Settings")

    # ────────────────────────────────────────────────────────────────────
    # Model Selector (UI Scaffolding)
    # ────────────────────────────────────────────────────────────────────
    # This dropdown is displayed but does NOT currently affect behavior.
    # It is scaffolding for a future feature (multi-model support).
    # The encode() function always uses the default model from src/config.py.
    #
    # In v0.3.1, this selector is purely for UI demonstration.
    # Future versions may wire this to actually pass the selected model to encode().

    selected_model = st.selectbox(
        label="LLM Model (Extraction)",
        options=["gpt-4", "gpt-3.5-turbo"],
        index=0,
        help=(
            "Model selector is scaffolding for future multi-model support. "
            "Currently, the app uses the model configured in src/config.py."
        ),
    )
    # NOTE: selected_model is assigned but not used in v0.3.1.
    # It exists to demonstrate configurability in the UI.

    # ────────────────────────────────────────────────────────────────────
    # "Show Raw CNL" Toggle
    # ────────────────────────────────────────────────────────────────────
    # Checkbox to control whether the raw CNL output is displayed in
    # the results section. This toggle is wired and functional.

    show_raw_cnl = st.checkbox(
        label="Show raw CNL",
        value=True,
        help="Display the raw Controlled Natural Language output from the encoder."
    )
    # NOTE: show_raw_cnl is used later in the results display section (v0.3.1b).

    # Visual divider within sidebar
    st.divider()

    # ────────────────────────────────────────────────────────────────────
    # About Section
    # ────────────────────────────────────────────────────────────────────
    # Project description and links to external resources.

    st.subheader("About")
    st.markdown(
        """
        **The Haiku Protocol** is a Controlled Natural Language (CNL)
        compression system that transforms verbose technical documentation
        into dense, machine-optimized strings while preserving 100% semantic meaning.

        It works like "minification" for natural language — compressing verbose
        prose to make LLM context more efficient.

        **Key Features:**
        - Lossless semantic compression (50%+ token savings)
        - Structure-preserving CNL encoding
        - Real-time compression metrics

        **Links:**
        - [GitHub Repository](https://github.com/your-org/haiku-protocol)
        - [Full Documentation](https://docs.example.com/haiku-protocol)
        - [Technical Paper](https://arxiv.example.com/haiku-protocol)
        """
    )

    # Version footer in sidebar
    st.caption("v0.3.1 — Streamlit UI Dev")
```

**Explanation:**
- Model selector is scaffolding only; it doesn't change behavior in v0.3.1.
- "Show raw CNL" toggle is functional and controls output display in later sections.
- About section provides context, key features, and external links.
- Links use placeholders; replace with actual URLs for production.

### 6. Footer Rendering

```python
# ============================================================================
# PAGE FOOTER
# ============================================================================
# Centered branding footer at the bottom of the page.

st.divider()

st.markdown(
    """
    <div style="text-align: center; color: #999; font-size: 0.9rem; margin-top: 2rem;">
        <p>Built with <span style="color: #e74c3c;">❤️</span> using Streamlit |
        The Haiku Protocol — Lossless Semantic Compression</p>
    </div>
    """,
    unsafe_allow_html=True,
)
```

**Explanation:**
- Footer is styled HTML centered at the bottom.
- Uses a light gray color (#999) to de-emphasize it visually.
- Heart emoji (❤️) adds a touch of personality.
- Footer text is informational and does not require interaction.

---

## File Structure

```
haiku-protocol/
└── src/
    └── app.py                 # Single-file Streamlit application
                              # (being built incrementally across v0.3.1a,
                              #  v0.3.1b, v0.3.1c)
```

No separate CSS files, no component libraries, no multi-page app. Everything lives in `src/app.py`.

---

## Implementation Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│              PAGE CONFIG & LAYOUT WORKFLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Create src/app.py                                      │
│  └─▶ Copy template imports, logging setup                       │
│                                                                 │
│  Step 2: Add st.set_page_config()                               │
│  └─▶ Set title, icon, wide layout                              │
│                                                                 │
│  Step 3: Inject custom CSS                                      │
│  └─▶ Define .main-header, .tagline, .metric-card classes       │
│                                                                 │
│  Step 4: Render header                                          │
│  └─▶ Display title and tagline with styled HTML                │
│                                                                 │
│  Step 5: Build sidebar                                          │
│  └─▶ Model selector (scaffolding)                               │
│  └─▶ "Show raw CNL" toggle                                      │
│  └─▶ About section with links                                   │
│                                                                 │
│  Step 6: Render footer                                          │
│  └─▶ Centered branding text                                     │
│                                                                 │
│  Step 7: Test in browser                                        │
│  └─▶ streamlit run src/app.py                                   │
│  └─▶ Verify layout, sidebar, header rendering                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Manual Testing Checklist

Since this is a UI component, testing is **manual and visual**, not automated via pytest. Use this checklist to verify each element:

| ✓ | Test Case | Expected Outcome | Notes |
|---|-----------|------------------|-------|
| [ ] | **Page Title in Browser Tab** | Browser tab shows "The Haiku Protocol" | Verify in browser tab title |
| [ ] | **Favicon in Browser Tab** | Browser tab shows "📦" icon | Should appear next to page title |
| [ ] | **Wide Layout Active** | Page uses full viewport width | No narrow centered column |
| [ ] | **Main Header Renders** | "📦 The Haiku Protocol" appears at top with large, bold styling | Should be ~2.5rem font size |
| [ ] | **Tagline Renders** | "Lossless Semantic Compression..." appears below header | Should be ~1.2rem font size, muted color |
| [ ] | **Header Divider** | Horizontal line appears after tagline | Provided by `st.divider()` |
| [ ] | **Sidebar Opens** | Sidebar toggle in top-left opens/closes sidebar | Default state: expanded |
| [ ] | **Settings Header in Sidebar** | "⚙️ Settings" header visible | Top of sidebar content |
| [ ] | **Model Selector Dropdown** | "LLM Model (Extraction)" dropdown appears with two options | Options: gpt-4, gpt-3.5-turbo |
| [ ] | **Model Selector Default** | Dropdown defaults to "gpt-4" | index=0 |
| [ ] | **Model Selector Has Help Text** | Hovering over dropdown shows help message about scaffolding | Help text explains it's UI-only |
| [ ] | **Show Raw CNL Checkbox** | Checkbox appears labeled "Show raw CNL" | Unchecked by default (value=True means checked) |
| [ ] | **Show Raw CNL Has Help Text** | Hovering over checkbox shows help text | Explains CNL output display |
| [ ] | **Sidebar Divider** | Horizontal line divides Settings from About section | Provided by `st.divider()` |
| [ ] | **About Section Header** | "About" subheader appears | Markdown h3 level |
| [ ] | **About Description Text** | Project description displays in sidebar | Multi-line markdown text |
| [ ] | **About Links Render** | Three links visible: GitHub, Documentation, Technical Paper | Links are markdown formatted |
| [ ] | **About Links Clickable** | Links open in new tab when clicked | Standard markdown link behavior |
| [ ] | **Version Caption in Sidebar** | "v0.3.1 — Streamlit UI Dev" appears at bottom of sidebar | Smaller font via `st.caption()` |
| [ ] | **Footer Divider** | Horizontal line appears above footer | At bottom of main content area |
| [ ] | **Footer Text Centered** | Footer text is centered horizontally | CSS `text-align: center` |
| [ ] | **Footer Text Color** | Footer text is light gray (#999) | Should be de-emphasized |
| [ ] | **Footer Heart Emoji** | Red heart emoji (❤️) appears in footer | Colored red (#e74c3c) |
| [ ] | **No Console Errors** | Browser DevTools console shows no JavaScript errors | Check browser console |
| [ ] | **No Streamlit Warnings** | Streamlit terminal output shows no warnings about missing components | Check terminal output |
| [ ] | **Mobile Responsiveness** | Layout adapts reasonably to smaller screen sizes | Streamlit's default responsiveness |

**Acceptance Criteria:** All checkboxes PASS before moving to v0.3.1b.

---

## Acceptance Criteria

The page configuration and layout sub-part is **complete** when ALL of the following conditions are met:

- [ ] `src/app.py` exists with all code from sections 1–6 above
- [ ] `st.set_page_config()` is called with correct title, icon, and wide layout
- [ ] Custom CSS with three classes (main-header, tagline, metric-card) is injected via `st.markdown(..., unsafe_allow_html=True)`
- [ ] Main header renders with emoji, project name, and bold, large styling
- [ ] Tagline renders directly below header with muted color
- [ ] Sidebar is visible with "⚙️ Settings" header
- [ ] Model selector dropdown appears in sidebar with two options (gpt-4, gpt-3.5-turbo)
- [ ] Model selector defaults to gpt-4 and includes help text explaining it is scaffolding
- [ ] "Show raw CNL" checkbox appears in sidebar and is checked by default
- [ ] "Show raw CNL" checkbox includes help text
- [ ] Sidebar divider separates Settings from About section
- [ ] About section displays project description and explanation
- [ ] Three links (GitHub, Documentation, Technical Paper) render in About section
- [ ] Version caption ("v0.3.1 — Streamlit UI Dev") appears at bottom of sidebar
- [ ] Footer divider appears at bottom of page
- [ ] Footer text is centered, light gray, and includes heart emoji
- [ ] App launches without console errors or Streamlit warnings
- [ ] Wide layout is visually confirmed (full-width, not narrow column)
- [ ] CSS classes render correctly (header is large/bold, tagline is muted, etc.)

---

## Limitations & Constraints

1. **No file-based CSS.** CSS is injected via Python string in `st.markdown()`. No separate `.css` file.
2. **Minimal theming.** Only three CSS classes. All other styling uses Streamlit's built-in defaults.
3. **No responsive breakpoints.** Streamlit's default responsiveness is used. No custom mobile-specific styling.
4. **Model selector is scaffolding.** The dropdown renders but does not affect the encode() call. It exists only for UI demonstration.
5. **Links are placeholders.** GitHub, Documentation, and Technical Paper links use example URLs. Update before production.
6. **Single-user, no auth.** No login, session management, or user-specific state. The sidebar settings apply to all users equally (if deployed).
7. **No dark mode.** Theming is light mode only. Streamlit's built-in dark mode toggle is available but not customized.

---

## Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| `streamlit` | ≥1.28.0 | Web framework for UI rendering |
| `src/encoder.py` | v0.2.0+ | Provides `encode()` function (imported, not yet used in v0.3.1a) |
| `src/validator.py` | v0.2.4+ | Provides `CompressionValidator` class (imported, not yet used in v0.3.1a) |

All dependencies should already be installed if `requirements.txt` is up to date from Phase 2.

---

## Outputs to Next Sub-Part

Upon completion of v0.3.1a, the following is ready for v0.3.1b (Input, Processing & Output):

1. **Page shell with header and footer.** The visual container is established.
2. **Sidebar infrastructure.** Settings, toggles, and About section are in place. The `show_raw_cnl` variable is available for downstream use.
3. **CSS classes defined.** The `.metric-card` class is ready to style metric sections in v0.3.1c.
4. **Imports and setup complete.** The `encode()` and `CompressionValidator` are imported and ready to use.

The next sub-part (v0.3.1b) will add:
- Input text area with default sample document
- Compress and Clear buttons
- Processing flow (spinner, error handling)
- Side-by-side results display

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|----------|-----------|--------|
| **PL-001** | Single-file Streamlit app (`src/app.py`) vs. multi-page app | Single-file keeps complexity low for a PoC. Multi-page is useful for larger apps but adds unnecessary structure here. | ✅ Approved |
| **PL-002** | CSS injection via `st.markdown()` vs. Streamlit native theming | Custom CSS gives full control over header/tagline/metric styling. Streamlit native theme API is more limited. Injected CSS is safe because we control all HTML content. | ✅ Approved |
| **PL-003** | Model selector as UI scaffolding vs. functional multi-model support | Including a non-functional UI element is acceptable for demonstration. It shows the interface is "designed for" multi-model support without requiring Phase 2 encoder changes. This avoids scope creep while maintaining a polished appearance. | ✅ Approved |
| **PL-004** | Wide layout vs. default centered layout | Wide layout allows the side-by-side results comparison (v0.3.1b) to be prominent and readable. It is the professional choice for a data-heavy demo. | ✅ Approved |

---

## Glossary

| Term | Definition |
|------|-----------|
| **Scaffolding** | A UI element that exists for demonstration but is not functionally wired. The model selector is scaffolding. |
| **CSS class** | A reusable style rule. We define three: `.main-header`, `.tagline`, `.metric-card`. |
| **`unsafe_allow_html`** | Streamlit parameter that allows rendering raw HTML/CSS. Safe here because we control the HTML; user input is never directly rendered as HTML. |
| **Sidebar** | Streamlit's left panel, accessed via `with st.sidebar:` context manager. |
| **Divider** | Horizontal line provided by `st.divider()`. Visual separation between sections. |

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Status:** ⬜ Not Started
**Next:** v0.3.1b — Input, Processing & Output Display
