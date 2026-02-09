# v0.4.1 — README & Quick Start

<aside>

**Version:** v0.4.1

**Parent:** v0.4.0 — Documentation & Release

**Status:** ⬜ Not Started

**Duration:** 45-60 minutes

**Deliverable:** Polished [README.md](http://README.md) with quick start guide

</aside>

---

## Objective

Create a README that **sells the project in 30 seconds** and provides clear setup instructions.

---

## README Structure

---

## Template: [README.md](http://README.md)

```markdown
# 📦 The Haiku Protocol

> **Lossless semantic compression for AI context windows.**
> Achieve **78% token reduction** while preserving 100% meaning.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

![Demo](./diagrams/demo.gif)

---

## 🎯 The Problem

LLM context windows are **expensive** and **finite**. Technical documentation wastes ~40% of tokens on grammatical "fluff"—articles, transitions, politeness markers.

**A 128k context window isn't 128k tokens of knowledge.** It's ~70k tokens of knowledge wrapped in 58k tokens of human-readable packaging.

---

## 💡 The Solution

The Haiku Protocol is a **Controlled Natural Language (CNL)** that "minifies" documentation for machine consumption—like how developers minify JavaScript for faster websites.

| Before (23 tokens) | After (10 tokens) |
| --- | --- |
| "To restart the server, you must first ensure that the configuration file is saved, and then you can execute the reboot command." | `Action:Restart_Server REQUIRES State:Config_Saved -> EXEC:Reboot_Cmd` |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key

### Installation

\`\`\`bash
# Clone the repository
git clone https://github.com/yourusername/haiku-protocol.git
cd haiku-protocol

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
\`\`\`

### Run the Demo

\`\`\`bash
streamlit run src/app.py
\`\`\`

Open http://localhost:8501 in your browser.

### Quick Test

\`\`\`python
from src.encoder import encode

result = encode("To restart the server, save your config first.")
print(f"Compressed: {result['haiku']}")
print(f"Savings: {result['savings_percent']}")
\`\`\`

---

## 📊 Benchmarks

| Metric | Haiku Protocol | LLMLingua | Improvement |
| --- | --- | --- | --- |
| Compression Ratio | 78% | 45% | +33% |
| Semantic Fidelity | 100% | 95% | +5% |
| Q&A Accuracy | 96% | 88% | +8% |

*Tested on procedural technical documentation. See `/benchmarks` for details.*

---

## 🏗️ Architecture

\`\`\`
Document → Chunker → Extractor → Synthesizer → CNL Output
             │           │            │
             │     (LLM-assisted)     │
             │           │            │
          [Split]   [Entities]    [Grammar]
\`\`\`

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system design.

---

## 📚 Documentation

- [Architecture Guide](./ARCHITECTURE.md) - System design
- [Style Guide](./STYLE_GUIDE.md) - CNL grammar specification
- [API Reference](./docs/API.md) - Module documentation

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) first.

\`\`\`bash
# Run tests
pytest

# Run linter
black src/ tests/
\`\`\`

---

## 📄 License

MIT License - see [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments

- [LangChain](https://langchain.com) for LLM orchestration
- [Microsoft LLMLingua](https://github.com/microsoft/LLMLingua) for benchmark comparison
- [Streamlit](https://streamlit.io) for the demo UI

---

<p align="center">
  Built with ❤️ by a Technical Writer who believes in the power of structured language.
</p>
```

---

## Checklist

- [ ]  Project name and tagline at top
- [ ]  Badges for license, Python version
- [ ]  Demo GIF or screenshot
- [ ]  Problem statement (concise)
- [ ]  Solution explanation
- [ ]  Quick Start section with copy-paste commands
- [ ]  Benchmark table with numbers
- [ ]  Architecture overview
- [ ]  Links to other docs
- [ ]  License statement

---

## Acceptance Criteria

- [ ]  [README.md](http://README.md) created and committed
- [ ]  All sections complete
- [ ]  Commands are copy-paste ready
- [ ]  No broken links
- [ ]  Renders correctly on GitHub