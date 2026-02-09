# v0.3.1 — Streamlit UI Development

<aside>

**Version:** v0.3.1

**Parent:** v0.3.0 — Demo & Visualization

**Status:** ⬜ Not Started

**Duration:** 60-90 minutes

**Deliverable:** [`app.py`](http://app.py) — Interactive Streamlit demo

</aside>

---

## Objective

Build a polished, interactive web UI that demonstrates the Haiku Protocol in action. This is your **portfolio showcase**.

---

## UI Components

---

## Implementation: [`app.py`](http://app.py)

```python
# src/app.py - Streamlit Demo Application

import streamlit as st
from encoder import encode
from validator import CompressionValidator

# Page configuration
st.set_page_config(
    page_title="The Haiku Protocol",
    page_icon="📦",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f1f1f;
    }
    .tagline {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">📦 The Haiku Protocol</p>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Lossless Semantic Compression for AI Context Windows</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    model = st.selectbox("LLM Model", ["gpt-4", "gpt-3.5-turbo"])
    show_raw = st.checkbox("Show raw CNL", value=True)
    st.divider()
    st.markdown("**About**")
    st.markdown("""
    The Haiku Protocol compresses technical documentation 
    into a Controlled Natural Language (CNL) optimized for 
    LLM context windows.
    
    [GitHub](https://github.com) | [Documentation](https://docs.com)
    """)

# Main content
st.header("1. 📝 Input Documentation")

# Sample text
default_text = """To restart the application server, you must first ensure that all configuration changes have been saved. This prevents any loss of settings during the reboot process.

Steps:
1. Navigate to the settings panel and click "Save Configuration"
2. Wait for the confirmation message to appear
3. Once confirmed, run the command: systemctl restart app-server

Warning: If you skip step 1, your recent changes may be lost."""

input_text = st.text_area(
    "Paste your documentation here:",
    value=default_text,
    height=200,
    help="Enter technical documentation to compress"
)

# Compress button
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    compress_btn = st.button("🗜️ Compress", type="primary", use_container_width=True)
with col2:
    clear_btn = st.button("🗑️ Clear", use_container_width=True)

if clear_btn:
    st.rerun()

# Processing
if compress_btn and input_text:
    with st.spinner("Encoding documentation..."):
        try:
            # Run encoder
            result = encode(input_text)
            
            st.success("✅ Compression complete!")
            
            # Results section
            st.header("2. 📊 Results")
            
            # Side-by-side comparison
            left_col, right_col = st.columns(2)
            
            with left_col:
                st.subheader("📄 Original")
                st.text_area(
                    "Original text",
                    value=input_text,
                    height=200,
                    disabled=True,
                    label_visibility="collapsed"
                )
                st.metric("Tokens", result["original_tokens"])
            
            with right_col:
                st.subheader("⚡ Haiku (Compressed)")
                st.code(result["haiku"], language="text")
                st.metric(
                    "Tokens", 
                    result["compressed_tokens"],
                    delta=f"-{result['token_savings']} saved",
                    delta_color="normal"
                )
            
            # Metrics section
            st.header("3. 📈 Compression Metrics")
            
            m1, m2, m3, m4 = st.columns(4)
            
            with m1:
                st.metric("Compression Ratio", result["savings_percent"])
            with m2:
                st.metric("Tokens Saved", result["token_savings"])
            with m3:
                st.metric("Original Size", f"{result['original_tokens']} tokens")
            with m4:
                st.metric("Compressed Size", f"{result['compressed_tokens']} tokens")
            
            # Progress bar visualization
            st.markdown("**Compression Visualization**")
            progress = result["compression_ratio"]
            st.progress(progress)
            st.caption(f"{result['savings_percent']} of tokens removed while preserving semantic meaning")
            
            # Celebration for good compression
            if result["compression_ratio"] >= 0.5:
                st.balloons()
            
        except Exception as e:
            st.error(f"❌ Encoding failed: {str(e)}")
            st.info("Make sure your OpenAI API key is configured in .env")

elif compress_btn:
    st.warning("⚠️ Please enter some text to compress")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    Built with ❤️ using Streamlit | The Haiku Protocol v1.0.0
</div>
""", unsafe_allow_html=True)
```

---

## Running the Demo

```bash
# From project root
cd haiku-protocol

# Activate environment
source haiku-env/bin/activate

# Run Streamlit
streamlit run src/app.py

# Opens browser at http://localhost:8501
```

---

## User Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                       USER FLOW                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. USER ARRIVES                                               │
│      └─▶ Sees header, tagline, sample text                      │
│                                                                 │
│   2. USER INPUTS TEXT                                           │
│      └─▶ Pastes documentation or uses sample                    │
│                                                                 │
│   3. USER CLICKS COMPRESS                                       │
│      └─▶ Spinner shows, API called                              │
│                                                                 │
│   4. RESULTS DISPLAYED                                          │
│      └─▶ Side-by-side comparison                                │
│      └─▶ Metrics cards                                          │
│      └─▶ Progress bar visualization                             │
│      └─▶ Celebration balloons (if >50%)                         │
│                                                                 │
│   5. USER ITERATES                                              │
│      └─▶ Try different inputs                                   │
│      └─▶ Adjust settings                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

- [ ]  [`app.py`](http://app.py) created in `src/` directory
- [ ]  App launches without errors
- [ ]  Input text area works
- [ ]  Compress button triggers encoding
- [ ]  Side-by-side display shows before/after
- [ ]  Metrics display correctly
- [ ]  Error handling for API failures
- [ ]  Responsive layout works