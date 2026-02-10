# v0.3.1b — Input, Processing & Output Display

<aside>

**Version:** v0.3.1b

**Parent:** v0.3.1 — Streamlit UI Development

**Status:** ⬜ Not Started

**Duration:** 25–35 minutes

**Deliverable:** Input text area, Compress/Clear buttons, processing flow with spinner, side-by-side results display, and error handling in `src/app.py`

</aside>

---

## Objective

Implement the interactive compression workflow. Users paste or edit documentation in a text area, click the Compress button, and see results side-by-side: the original text with its token count on the left, the compressed CNL with its token count and savings delta on the right. The processing flow includes a spinner to indicate work in progress, error handling to catch API failures gracefully, and input validation to warn about empty submissions. This sub-part is the "heart" of the demo — where the encoder pipeline's output becomes visible.

---

## User Stories

**Story 1: User Compresses Documentation and Sees Results**

> As a technical user, I want to paste a multi-paragraph procedure into the text area and click the Compress button so that I immediately see the compressed CNL output side-by-side with the original, understanding at a glance how much compression was achieved.

**Story 2: User Encounters API Error and Receives Helpful Guidance**

> As a user whose API key is misconfigured, I want to see a clear error message when compression fails so that I can understand the problem and take corrective action (check my .env file, verify my API key, etc.) rather than being left confused.

---

## Implementation Design

This section covers the Python code for input handling, button interaction, processing flow, results display, and error handling. This code follows immediately after the footer from v0.3.1a and comprises the bulk of the application logic.

### 1. Default Sample Document

The app includes a hardcoded default sample document that demonstrates the compression pipeline on load. This is the "restart server" procedure referenced throughout the project:

```python
# ============================================================================
# DEFAULT SAMPLE DOCUMENT
# ============================================================================
# Hardcoded sample text that appears in the text area on page load.
# This is based on the "restart server" procedure from the project documentation.
#
# Rationale for hardcoding:
# - Ensures a known, representative example is always available
# - Reduces file I/O and complexity (no external file to manage)
# - Makes the demo self-contained and deployable anywhere
# - User can replace the text or clear and paste their own

DEFAULT_SAMPLE_DOCUMENT = """To restart the server, you must first ensure that all configuration changes have been saved. This prevents any loss of settings during the reboot process.

Steps to follow:
1. Navigate to the Settings page and click "Save Configuration"
2. Wait for the confirmation message to appear (this usually takes 5-10 seconds)
3. Once confirmed, open a terminal and run the command: systemctl restart app-server
4. The server will restart automatically; you may see a brief connection loss

Warning: If you skip step 1 and reboot without saving, your recent configuration changes will be lost. This is a critical mistake that could affect production systems.

Additional Notes:
- The restart process typically takes 30-60 seconds to complete
- You can monitor progress in the system logs if needed
- No manual cleanup is required after the restart completes"""
```

**Explanation:**
- Multi-paragraph document with headers, numbered list, warnings, and notes
- Realistic procedural documentation that benefits from compression
- Hardcoded as a module-level constant for easy access
- Users can edit, replace, or clear this text and enter their own

### 2. Input Section with Text Area and Buttons

```python
# ============================================================================
# INPUT SECTION
# ============================================================================
# Users paste or edit documentation in a text area. The default sample
# document appears on load. Two buttons: Compress (primary) and Clear.

st.header("1. 📝 Input Documentation")
st.markdown(
    "Paste your technical documentation below to compress it using the Haiku Protocol:"
)

# Text area for input
input_text = st.text_area(
    label="Documentation Input",
    value=DEFAULT_SAMPLE_DOCUMENT,
    height=250,
    help="Enter or paste technical documentation (markdown, plain text, etc.). No file upload needed.",
    label_visibility="collapsed",  # Hide redundant label
)

# Buttons in a three-column layout
col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    compress_btn = st.button(
        label="🗜️ Compress",
        type="primary",
        use_container_width=True,
        help="Click to compress the input documentation using the Haiku Protocol encoder.",
    )

with col2:
    clear_btn = st.button(
        label="🗑️ Clear",
        use_container_width=True,
        help="Clear the input text area and reset the results.",
    )

# col3 is empty (spacer) for visual balance
```

**Explanation:**
- `st.text_area()` with default sample doc, 250px height, and helpful label
- `label_visibility="collapsed"` hides the redundant "Documentation Input" label
- Two buttons in columns [1, 1, 3] so they are compact and the spacer fills remaining width
- Compress button is `type="primary"` (blue, prominent)
- Clear button is default styling (less prominent)
- Both buttons have hover help text explaining their function

### 3. Clear Button Handler

```python
# ============================================================================
# CLEAR BUTTON HANDLER
# ============================================================================
# When the Clear button is clicked, reset the entire app state by calling
# st.rerun(). This causes the entire script to re-execute from the top.
# The text area will reset to the default sample document.
# Any results or errors will disappear.

if clear_btn:
    st.rerun()
```

**Explanation:**
- `st.rerun()` re-executes the entire Streamlit script from the beginning
- This resets all session state and clears any previous results
- Simple and idiomatic for Streamlit (no complex state management needed)

### 4. Input Validation and Empty Check

```python
# ============================================================================
# COMPRESS BUTTON HANDLER — INPUT VALIDATION
# ============================================================================
# When Compress is clicked, first validate that input is not empty.
# If empty, show a warning. If not empty, proceed to processing.

if compress_btn:
    # Trim whitespace for validation
    trimmed_input = input_text.strip()

    if not trimmed_input:
        # Empty or whitespace-only input
        st.warning(
            "⚠️ Please enter some text to compress. "
            "The input field is empty or contains only whitespace."
        )
    else:
        # Input is valid; proceed to processing
        # (Logic continues below in the Processing Flow section)
        pass  # Placeholder; will be replaced with encoding logic
```

**Explanation:**
- `input_text.strip()` removes leading/trailing whitespace for validation
- Empty check prevents meaningless API calls
- `st.warning()` displays a warning message in the UI
- Clear, actionable message guides the user

### 5. Processing Flow with Spinner

```python
# ============================================================================
# COMPRESS BUTTON HANDLER — PROCESSING FLOW
# ============================================================================
# When Compress is clicked and input is valid, wrap the encode() call
# in a st.spinner() to show a loading indicator. This signals to the user
# that work is in progress and prevents duplicate clicks.

if compress_btn and input_text.strip():
    # Show loading spinner while encoding
    with st.spinner("🔄 Encoding documentation..."):
        try:
            # ────────────────────────────────────────────────────────────
            # CALL THE ENCODER
            # ────────────────────────────────────────────────────────────
            # The encode() function from src/encoder.py is called with the
            # input text. It returns a dict with the expected schema:
            #
            #   {
            #       "haiku": str,              # Compressed CNL string
            #       "original": str,           # Original input text
            #       "original_tokens": int,    # Token count of original
            #       "compressed_tokens": int,  # Token count of compressed
            #       "compression_ratio": float, # 0.0 to 1.0
            #       "savings_percent": str,    # e.g., "56%"
            #       "token_savings": int       # original_tokens - compressed_tokens
            #   }
            #
            # If encode() returns an unexpected schema, this code will fail
            # and raise a KeyError, which is caught in the except clause below.

            result = encode(input_text)

            # ────────────────────────────────────────────────────────────
            # SUCCESS: Display results
            # ────────────────────────────────────────────────────────────
            st.success("✅ Compression complete! Results below.")

            # Store result in session state for use by the results section
            # This ensures the result persists even if the user clicks Compress again
            # Session state is Streamlit's built-in state management
            st.session_state.last_result = result
            st.session_state.has_result = True

        except KeyError as e:
            # ────────────────────────────────────────────────────────────
            # ERROR: Unexpected encode() return schema
            # ────────────────────────────────────────────────────────────
            st.error(
                f"❌ Encoding error: Unexpected response format from encoder. "
                f"Missing field: {str(e)}"
            )
            st.info(
                "This is an internal error. Please verify that src/encoder.py "
                "returns the expected schema with fields: haiku, original, "
                "original_tokens, compressed_tokens, compression_ratio, "
                "savings_percent, token_savings."
            )
            logger.exception("KeyError in encode result schema", exc_info=e)

        except Exception as e:
            # ────────────────────────────────────────────────────────────
            # ERROR: General exception from encode() or other issues
            # ────────────────────────────────────────────────────────────
            # Common causes:
            # - OpenAI API key is missing, invalid, or expired
            # - API rate limits exceeded
            # - Network error or API unavailable
            # - Invalid input format that encoder cannot handle

            st.error(
                f"❌ Encoding failed: {str(e)}"
            )
            st.info(
                "**Troubleshooting:**\n"
                "1. Verify that `OPENAI_API_KEY` is set in your `.env` file\n"
                "2. Check that your API key is valid and not expired\n"
                "3. Ensure you have sufficient API quota\n"
                "4. Try with a shorter input if the error persists\n"
                "\n"
                "If the problem continues, check the terminal logs for more details."
            )
            logger.exception("Exception during encoding", exc_info=e)
```

**Explanation:**
- `st.spinner()` context manager displays a loading indicator
- Spinner message is clear: "🔄 Encoding documentation..."
- `try/except` wraps the `encode()` call
- Two exception types are caught separately: `KeyError` (schema mismatch) and general `Exception` (API errors)
- `st.success()` displays a green success banner on successful compression
- Error messages are user-friendly and include troubleshooting guidance
- `st.info()` provides extended help text
- `logger.exception()` logs full stack traces for debugging
- Result is stored in `st.session_state` for persistence across reruns

---

### 6. Results Section — Side-by-Side Display

After successful compression, the results section displays the original and compressed documents side-by-side with token counts and savings information. This code executes if `st.session_state.has_result` is True:

```python
# ============================================================================
# RESULTS SECTION
# ============================================================================
# Display side-by-side original vs. compressed output with token metrics.
# This section appears only after successful compression.

if "has_result" in st.session_state and st.session_state.has_result:
    result = st.session_state.last_result

    st.header("2. 📊 Results")
    st.markdown(
        "**Original** (left) vs. **Haiku Compressed** (right) — side-by-side comparison"
    )

    # Create two-column layout for side-by-side display
    left_col, right_col = st.columns(2)

    # ────────────────────────────────────────────────────────────────────
    # LEFT COLUMN: ORIGINAL TEXT
    # ────────────────────────────────────────────────────────────────────

    with left_col:
        st.subheader("📄 Original Document")

        # Display original text in a disabled (read-only) text area
        st.text_area(
            label="Original text (read-only)",
            value=result["original"],
            height=300,
            disabled=True,  # User cannot edit; for display only
            label_visibility="collapsed",
        )

        # Token count metric for original
        st.metric(
            label="Original Tokens",
            value=result["original_tokens"],
            help="Total token count of the original document"
        )

    # ────────────────────────────────────────────────────────────────────
    # RIGHT COLUMN: COMPRESSED TEXT
    # ────────────────────────────────────────────────────────────────────

    with right_col:
        st.subheader("⚡ Haiku Compressed")

        # Display compressed CNL in a code block
        # Code block is ideal for monospace display of CNL syntax
        st.code(
            result["haiku"],
            language="text",
        )

        # Token count metric for compressed with delta showing savings
        st.metric(
            label="Compressed Tokens",
            value=result["compressed_tokens"],
            delta=f"-{result['token_savings']} saved",
            delta_color="normal",  # "normal" keeps delta neutral; "inverse" would reverse red/green
            help="Token count of the compressed CNL output"
        )
```

**Explanation:**
- Results section is conditional: only appears if `st.session_state.has_result` is True
- Header and subheader introduce the comparison
- Two columns created via `st.columns(2)`
- Left column shows original text in a disabled text area (read-only)
- Right column shows compressed CNL in a code block (monospace rendering)
- Token count metrics display for both original and compressed
- Delta shows tokens saved (e.g., "-45 saved"), displayed in neutral color
- If `show_raw_cnl` toggle from the sidebar is False, this section could be hidden (see note below)

**Optional Enhancement — Conditional CNL Display:**

If you want to respect the `show_raw_cnl` toggle from the sidebar, wrap the right column in a conditional:

```python
    with right_col:
        st.subheader("⚡ Haiku Compressed")

        # Only show compressed output if the "Show raw CNL" toggle is checked
        if show_raw_cnl:
            st.code(result["haiku"], language="text")
        else:
            st.info("Raw CNL output is hidden. Toggle 'Show raw CNL' in the sidebar to display.")

        st.metric(
            label="Compressed Tokens",
            value=result["compressed_tokens"],
            delta=f"-{result['token_savings']} saved",
            delta_color="normal",
            help="Token count of the compressed CNL output"
        )
```

(This enhancement is recommended for full feature integration.)

---

## Default Sample Document (Full Content)

The hardcoded sample document used throughout this sub-part is:

```
To restart the server, you must first ensure that all configuration changes
have been saved. This prevents any loss of settings during the reboot process.

Steps to follow:
1. Navigate to the Settings page and click "Save Configuration"
2. Wait for the confirmation message to appear (this usually takes 5-10 seconds)
3. Once confirmed, open a terminal and run the command: systemctl restart app-server
4. The server will restart automatically; you may see a brief connection loss

Warning: If you skip step 1 and reboot without saving, your recent configuration
changes will be lost. This is a critical mistake that could affect production systems.

Additional Notes:
- The restart process typically takes 30-60 seconds to complete
- You can monitor progress in the system logs if needed
- No manual cleanup is required after the restart completes
```

This document is:
- Representative of technical documentation (procedure with steps)
- Long enough to demonstrate meaningful compression (200+ tokens)
- Contains structure (headers, lists, warnings, notes)
- Based on the canonical "restart server" example used throughout the project

---

## encode() API Contract

The `encode()` function from `src/encoder.py` is expected to return a dictionary with the following schema:

```python
{
    "haiku": str,              # Compressed CNL string (dense, structured)
    "original": str,           # Original input text (echoed back)
    "original_tokens": int,    # Token count of original document
    "compressed_tokens": int,  # Token count of compressed CNL
    "compression_ratio": float, # Calculated as (original - compressed) / original, range [0.0, 1.0]
    "savings_percent": str,    # Formatted percentage, e.g., "56%" or "0.56"
    "token_savings": int       # Calculated as original_tokens - compressed_tokens
}
```

**Expected Behavior:**
- `compress_ratio` should be in range [0.0, 1.0], representing the fraction of tokens removed
- `savings_percent` should be a human-readable percentage string (e.g., "45.2%")
- `token_savings` should equal `original_tokens - compressed_tokens`
- `haiku` should be a valid CNL string (may contain REQUIRES, EXEC, State:, Action:, etc.)
- `original` should match the input passed to `encode()`

**If encode() returns an unexpected schema:**
- A `KeyError` exception is raised (caught in exception handler)
- User sees: "Unexpected response format from encoder"
- Log entry is created for debugging

---

## Error Handling Matrix

This table documents all error cases and their handling:

| Error Case | Trigger | User-Visible Message | Log Action | Actionable? |
|-----------|---------|----------------------|------------|-----------|
| **Empty Input** | User clicks Compress with empty text area | ⚠️ "Please enter some text to compress." | None (expected) | Yes — user edits text |
| **API Key Missing** | `OPENAI_API_KEY` not in `.env` or environment | ❌ "Encoding failed: [error message]" + info box with troubleshooting | `logger.exception()` | Yes — user checks .env |
| **API Key Invalid** | `OPENAI_API_KEY` is incorrect or expired | ❌ "Encoding failed: Invalid API key" | `logger.exception()` | Yes — user regenerates API key |
| **API Rate Limit** | Quota exceeded on OpenAI account | ❌ "Encoding failed: Rate limit exceeded" | `logger.exception()` | Yes — user waits or upgrades quota |
| **Network Error** | Network unavailable or OpenAI API unreachable | ❌ "Encoding failed: Connection error" | `logger.exception()` | Yes — user checks network |
| **Unexpected encode() Schema** | `encode()` returns dict missing expected fields | ❌ "Encoding error: Unexpected response format..." | `logger.exception()` | Partially — indicates Phase 2 bug |
| **Timeout** | encode() takes too long (e.g., LLM API slow) | ❌ "Encoding failed: Request timeout" | `logger.exception()` | Yes — user retries or checks API status |
| **Malformed Input** | Input contains characters that break encoding | ❌ "Encoding failed: Invalid input format" | `logger.exception()` | Possibly — user simplifies input |

---

## File Structure

```
haiku-protocol/
└── src/
    └── app.py                 # Single file, now including:
                              #   - v0.3.1a: page config, sidebar
                              #   - v0.3.1b: input, processing, output
                              #   - v0.3.1c: metrics (added later)
```

All code from v0.3.1a remains; v0.3.1b adds input/processing/output code sequentially.

---

## Implementation Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│         INPUT, PROCESSING & OUTPUT WORKFLOW                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: Define DEFAULT_SAMPLE_DOCUMENT constant               │
│  └─▶ Multi-paragraph procedure document                        │
│                                                                 │
│  Step 2: Create Input Section                                  │
│  └─▶ st.text_area() with default sample doc                    │
│  └─▶ Compress button (primary)                                 │
│  └─▶ Clear button                                              │
│                                                                 │
│  Step 3: Implement Clear Button Handler                         │
│  └─▶ Calls st.rerun() to reset app state                       │
│                                                                 │
│  Step 4: Implement Compress Button Handler                      │
│  └─▶ Check if input is not empty                               │
│  └─▶ If empty: show warning                                    │
│  └─▶ If valid: proceed to processing                           │
│                                                                 │
│  Step 5: Wrap encode() in st.spinner()                         │
│  └─▶ Show "Encoding documentation..." message                  │
│  └─▶ Call encode(input_text)                                   │
│  └─▶ Catch KeyError and general Exception separately           │
│                                                                 │
│  Step 6: Handle Success                                         │
│  └─▶ Display st.success() banner                               │
│  └─▶ Store result in st.session_state                          │
│                                                                 │
│  Step 7: Handle Errors                                          │
│  └─▶ Display st.error() with clear message                     │
│  └─▶ Display st.info() with troubleshooting guidance            │
│  └─▶ Log exception to logger                                   │
│                                                                 │
│  Step 8: Implement Results Section                              │
│  └─▶ Conditional: check st.session_state.has_result             │
│  └─▶ Two-column layout (original vs. compressed)               │
│  └─▶ Left: disabled text area + token metric                   │
│  └─▶ Right: code block + token metric with delta               │
│                                                                 │
│  Step 9: Test end-to-end                                        │
│  └─▶ streamlit run src/app.py                                   │
│  └─▶ Enter sample text or paste custom docs                    │
│  └─▶ Click Compress, verify results display                    │
│  └─▶ Click Clear, verify state reset                           │
│  └─▶ Test with empty input (should warn)                       │
│  └─▶ Simulate API error (comment out API key) and verify error  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Manual Testing Checklist

| ✓ | Test Case | Expected Outcome | Notes |
|---|-----------|------------------|-------|
| [ ] | **Input Section Header** | "1. 📝 Input Documentation" appears | Markdown h2 header |
| [ ] | **Input Description Text** | Guidance text appears above text area | Encourages user to paste docs |
| [ ] | **Text Area Renders** | Large text input field appears with default sample | 250px height, label hidden |
| [ ] | **Default Sample Text** | Default "restart server" procedure fills text area on page load | Text is fully visible and readable |
| [ ] | **User Can Edit Text** | User can click in text area and modify/replace text | Text area is enabled (not disabled) |
| [ ] | **Compress Button Visible** | "🗜️ Compress" button appears | Primary button, blue, prominent |
| [ ] | **Clear Button Visible** | "🗑️ Clear" button appears | Default styling, next to Compress |
| [ ] | **Compress Button Hover Help** | Hovering shows help text about compression | Tooltip explains button function |
| [ ] | **Clear Button Hover Help** | Hovering shows help text about clearing | Tooltip explains button function |
| [ ] | **Button Layout** | Buttons are compact (not full width) | Column layout [1, 1, 3] gives balance |
| [ ] | **Empty Input Warning** | Clicking Compress with empty text shows warning | Warning message: "Please enter some text to compress" |
| [ ] | **Warning Styling** | Warning displays in yellow/orange | Streamlit default warning color |
| [ ] | **Loading Spinner** | Clicking Compress shows "🔄 Encoding documentation..." spinner | Spinner appears during API call |
| [ ] | **Success Banner** | After successful compression, green banner appears | "✅ Compression complete! Results below." |
| [ ] | **Results Section Header** | "2. 📊 Results" appears after success | Markdown h2 header |
| [ ] | **Results Comparison Text** | Description of side-by-side comparison appears | Explains original vs. Haiku |
| [ ] | **Two-Column Layout** | Original on left, Compressed on right | Columns are equal width |
| [ ] | **Original Subheader** | "📄 Original Document" appears on left | Markdown h3 header |
| [ ] | **Original Text Displays** | Original input text appears in disabled text area | 300px height, not editable |
| [ ] | **Original Token Metric** | "Original Tokens" metric card displays token count | Number is positive integer |
| [ ] | **Compressed Subheader** | "⚡ Haiku Compressed" appears on right | Markdown h3 header |
| [ ] | **Compressed Code Block** | CNL output displays in monospace code block | Readable, structured CNL output |
| [ ] | **Compressed Token Metric** | "Compressed Tokens" metric displays token count | Number is positive, less than original |
| [ ] | **Savings Delta** | Delta shows "-X saved" (e.g., "-45 saved") | Neutral color, not red/green |
| [ ] | **Clear Button Resets** | Clicking Clear button resets app to initial state | Results disappear, text area shows sample doc again |
| [ ] | **Multiple Compressions** | User can compress different texts multiple times | Each new compression replaces previous results |
| [ ] | **API Key Error** | Commenting out API key and clicking Compress shows error | Error message appears with troubleshooting |
| [ ] | **Error Message Clear** | Error message is user-friendly and actionable | Suggests checking .env file, API key validity |
| [ ] | **Extended Help on Error** | Info box with troubleshooting steps appears below error | Bulleted list of diagnostic steps |
| [ ] | **No Console Errors** | Browser console shows no JavaScript errors | Check browser DevTools |
| [ ] | **Logs Contain Exception Data** | Terminal logs show exception traceback on error | `logger.exception()` output is readable |
| [ ] | **Session State Persists** | Results remain visible if user scrolls or interacts with sidebar | `st.session_state` maintains state across reruns |
| [ ] | **Show Raw CNL Toggle Works** | If implemented: toggling sidebar checkbox hides/shows CNL | Conditional display in right column |

**Acceptance Criteria:** All checkboxes PASS before moving to v0.3.1c.

---

## Acceptance Criteria

The input, processing & output sub-part is **complete** when ALL of the following conditions are met:

- [ ] `src/app.py` includes all code from v0.3.1a plus v0.3.1b sections
- [ ] `DEFAULT_SAMPLE_DOCUMENT` constant is defined with multi-paragraph restart procedure
- [ ] Input section has "1. 📝 Input Documentation" header
- [ ] `st.text_area()` displays default sample document on page load
- [ ] Compress button (🗜️) is primary-styled and functional
- [ ] Clear button (🗑️) is default-styled and functional
- [ ] Clear button calls `st.rerun()` and resets all state
- [ ] Empty input shows warning message via `st.warning()`
- [ ] Valid input triggers `st.spinner("🔄 Encoding documentation...")`
- [ ] `encode()` is called inside try/except block
- [ ] Successful compression displays `st.success()` banner
- [ ] Successful result is stored in `st.session_state.last_result`
- [ ] Results section has "2. 📊 Results" header and appears only after success
- [ ] Results section displays in two-column layout (original left, compressed right)
- [ ] Left column shows original text in disabled `st.text_area()`
- [ ] Left column displays "Original Tokens" metric with correct count
- [ ] Right column shows compressed CNL in `st.code()` block
- [ ] Right column displays "Compressed Tokens" metric with delta showing savings
- [ ] `KeyError` exception catches schema mismatches and displays informative error
- [ ] General `Exception` catches API errors and displays troubleshooting guidance
- [ ] Error messages include `st.info()` box with actionable troubleshooting steps
- [ ] Logger records full exception traces for debugging
- [ ] Result dict contains all expected fields: haiku, original, original_tokens, compressed_tokens, compression_ratio, savings_percent, token_savings
- [ ] Sidebar `show_raw_cnl` toggle is available for use in conditional display (optional v0.3.1b enhancement)
- [ ] App handles multiple compression cycles without state corruption
- [ ] No console errors or warnings on successful compression
- [ ] API errors are caught and handled gracefully (no crash)

---

## Limitations & Constraints

1. **No async processing.** Compression is synchronous; UI blocks during API call. The spinner indicates this to the user.
2. **No caching.** Each compression is a fresh API call. Caching would mask real-world latency.
3. **No file upload.** Text input only; no drag-and-drop, file upload, or URL fetching.
4. **Single compression per session.** Results are replaced each time Compress is clicked. No history or saved results.
5. **Input validation is basic.** Only checks for empty/whitespace. No length limits, encoding validation, or content-type checks.
6. **Error messages are generic.** Error text comes directly from the exception. No custom error codes or structured logging (that's Phase 4).
7. **No rate-limiting on UI side.** Users can click Compress repeatedly. Rate-limit errors are handled by catching the exception.
8. **Mobile display.** Results columns may stack on very small screens due to Streamlit's responsiveness. Not explicitly optimized for mobile.

---

## Dependencies

| Dependency | Version | Purpose |
|-----------|---------|---------|
| `streamlit` | ≥1.28.0 | `st.text_area()`, `st.spinner()`, `st.success()`, `st.error()`, `st.info()`, `st.session_state` |
| `src/encoder.py` | v0.2.0+ | `encode(text)` function that returns compression result dict |
| `src/validator.py` | v0.2.4+ | `CompressionValidator` class (imported but not directly used in v0.3.1b; available for v0.3.1c) |
| `logging` | stdlib | `logger.exception()` for error logging |
| `typing` | stdlib | Type hints (Optional, Dict, Any) |

---

## Outputs to Next Sub-Part

Upon completion of v0.3.1b, the following is ready for v0.3.1c (Metrics Dashboard):

1. **Successful compression results.** The `result` dict from `encode()` is available in `st.session_state.last_result`.
2. **All required metrics.** Result contains `compression_ratio`, `token_savings`, `original_tokens`, `compressed_tokens`, and `savings_percent`.
3. **Conditional display infrastructure.** Code is structured with `if "has_result" in st.session_state` checks, making it easy to add metrics sections.
4. **Sidebar toggle available.** The `show_raw_cnl` variable from v0.3.1a is available for conditional metric display (optional).

The next sub-part (v0.3.1c) will add:
- Four-column metric cards (compression ratio, tokens saved, original size, compressed size)
- Progress bar visualization of compression ratio
- Celebration animation (`st.balloons()`) when compression ≥ 50%
- Optional: raw CNL display in expander (if `show_raw_cnl` is True)

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|----------|-----------|--------|
| **IP-001** | Hardcoded default sample document vs. file-loaded | Hardcoding simplifies deployment and eliminates file I/O. Every user sees the same representative example. User can replace with custom text. | ✅ Approved |
| **IP-002** | `st.text_area()` for display vs. `st.code()` | `st.text_area()` is the natural input container. `st.code()` is reserved for the CNL output (monospace, read-only). | ✅ Approved |
| **IP-003** | `st.rerun()` for Clear vs. session state manipulation | `st.rerun()` is simple and idiomatic for Streamlit. Full reset is cleaner than selective state clearing. | ✅ Approved |
| **IP-004** | Two exception types (KeyError + Exception) vs. generic catch | KeyError is a schema contract violation (Phase 2 bug); Exception covers API and runtime issues (user-actionable). Separate handling allows specific messaging. | ✅ Approved |
| **IP-005** | Side-by-side layout vs. stacked layout | Side-by-side emphasizes before/after comparison and uses wide layout effectively. Stacked is harder to read on large screens. | ✅ Approved |
| **IP-006** | Store result in `st.session_state` vs. local variable | Session state persists across reruns (e.g., if sidebar is toggled). Local variables are lost on rerun. Session state is necessary for the app to function correctly. | ✅ Approved |
| **IP-007** | Display original in disabled text area vs. plain text | Disabled text area is a familiar UI pattern and allows word wrap, line numbers, and height adjustments. Plain text is less interactive. | ✅ Approved |
| **IP-008** | Display compressed in `st.code()` vs. `st.text_area()` | CNL is code-like and benefits from monospace. Code block indicates it's not user-editable. Text area would suggest the user can edit it. | ✅ Approved |

---

## Glossary

| Term | Definition |
|------|-----------|
| **st.text_area()** | Streamlit multi-line text input component. Can be disabled for display-only. |
| **st.spinner()** | Streamlit context manager that shows a loading indicator while code executes. |
| **st.success()** | Streamlit green success banner. |
| **st.error()** | Streamlit red error banner. |
| **st.info()** | Streamlit blue information banner (informational, not an error). |
| **st.session_state** | Streamlit's built-in state dictionary that persists across script reruns within a single user session. |
| **st.rerun()** | Streamlit function that re-executes the entire script from top to bottom. Used to reset UI state. |
| **st.code()** | Streamlit code block component. Renders text in monospace with syntax highlighting (optional). |
| **encode()** | Function from `src/encoder.py` that compresses text and returns a result dict. |
| **CNL** | Controlled Natural Language. The dense, structured output format of the encoder. |
| **Delta** | The change/difference indicator shown next to the Compressed Tokens metric (e.g., "-45 saved"). |

---

**Document Version:** 1.0
**Last Updated:** 2026-02-09
**Status:** ⬜ Not Started
**Next:** v0.3.1c — Metrics Dashboard & Celebration
