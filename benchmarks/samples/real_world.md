# DataForge — Data Transformation Library

DataForge is a lightweight Python library for transforming, validating, and
exporting structured data. It supports CSV, JSON, and Parquet formats with
built-in schema validation and extensible transform pipelines.

## Features

- **Format-agnostic** — Read and write CSV, JSON, Parquet, and YAML
- **Schema validation** — Define schemas with type constraints and nullable rules
- **Transform pipelines** — Chain transforms with built-in error recovery
- **Streaming support** — Process files larger than available memory
- **Extensible** — Write custom transforms and validators as plugins

## Installation

Install from PyPI:

```bash
pip install dataforge
```

Or install from source for development:

```bash
git clone https://github.com/example/dataforge.git
cd dataforge
pip install -e ".[dev]"
```

### Requirements

- Python 3.9 or later
- pandas ≥ 2.0
- pyarrow ≥ 12.0 (for Parquet support)

## Quick Start

### Basic Usage

```python
from dataforge import Pipeline, read_csv

data = read_csv("input.csv")
pipeline = Pipeline([
    ("rename", {"old": "col_a", "new": "column_alpha"}),
    ("filter", {"column": "status", "value": "active"}),
    ("cast", {"column": "amount", "dtype": "float"}),
])
result = pipeline.run(data)
result.to_json("output.json")
```

### Schema Validation

Define a schema to validate data before processing:

```python
from dataforge import Schema, Field

schema = Schema([
    Field("id", dtype="int", nullable=False, unique=True),
    Field("name", dtype="str", max_length=100),
    Field("email", dtype="str", pattern=r"^[\w.]+@[\w.]+$"),
    Field("amount", dtype="float", min_value=0.0),
])

errors = schema.validate(data)
if errors:
    for err in errors:
        print(f"Row {err.row}: {err.message}")
```

## API Reference

### Pipeline

The `Pipeline` class chains multiple transforms together:

| Method           | Description                              |
| ---------------- | ---------------------------------------- |
| `run(data)`      | Execute all transforms sequentially      |
| `add(transform)` | Append a transform to the pipeline       |
| `validate()`     | Check that all transforms are compatible |
| `summary()`      | Print a human-readable summary of steps  |

### Transforms

Built-in transforms available out of the box:

| Transform | Parameters            | Description              |
| --------- | --------------------- | ------------------------ |
| `rename`  | `old`, `new`          | Rename a column          |
| `filter`  | `column`, `value`     | Keep rows matching value |
| `cast`    | `column`, `dtype`     | Change column data type  |
| `drop`    | `columns`             | Remove specified columns |
| `fill_na` | `column`, `value`     | Replace missing values   |
| `sort`    | `column`, `ascending` | Sort by column           |

### Error Handling

DataForge uses structured error objects:

```python
from dataforge.errors import TransformError, ValidationError

try:
    result = pipeline.run(data)
except TransformError as e:
    print(f"Transform '{e.step}' failed: {e.message}")
    print(f"Affected rows: {e.row_count}")
```

## Configuration

### Environment Variables

| Variable                | Default              | Description                              |
| ----------------------- | -------------------- | ---------------------------------------- |
| `DATAFORGE_CACHE_DIR`   | `~/.dataforge/cache` | Cache directory for intermediate results |
| `DATAFORGE_LOG_LEVEL`   | `WARNING`            | Logging verbosity                        |
| `DATAFORGE_MAX_WORKERS` | `4`                  | Parallel processing threads              |

### Configuration File

Create a `dataforge.toml` in your project root:

```toml
[pipeline]
max_retries = 3
fail_fast = false

[logging]
level = "INFO"
format = "%(asctime)s %(levelname)s %(message)s"
```

## Contributing

### Development Setup

```bash
git clone https://github.com/example/dataforge.git
cd dataforge
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

### Running Tests

```bash
pytest tests/ -v --cov=dataforge
```

### Code Style

This project uses `ruff` for linting and `black` for formatting:

```bash
ruff check src/
black --check src/ tests/
```

## License

DataForge is released under the MIT License. See [LICENSE](LICENSE) for details.
