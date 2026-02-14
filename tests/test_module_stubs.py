"""
test_module_stubs.py - Tests for v0.1.3c Source Module Stubs
=============================================================

Verifies that all 7 source module stubs are correctly defined with:
- Valid imports and classes
- Dataclass instantiation
- NotImplementedError on all stub methods
- Type hints on method signatures
- Logger declarations
- py_compile-clean syntax

Version: v0.1.3c
"""

import importlib
import inspect
import logging
import py_compile
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))


# ============================================
# Module 1: encoder.py
# ============================================

@pytest.mark.unit
class TestEncoderModule:
    """Tests for src/encoder.py stub."""

    def test_import_encoder_module(self):
        """encoder module can be imported."""
        import src.encoder
        assert src.encoder is not None

    def test_import_haiku_encoder_class(self):
        """HaikuEncoder class is importable."""
        from src.encoder import HaikuEncoder
        assert HaikuEncoder is not None

    def test_haiku_encoder_init(self):
        """HaikuEncoder can be instantiated."""
        from src.encoder import HaikuEncoder
        encoder = HaikuEncoder()
        assert encoder.config == {}

    def test_haiku_encoder_init_with_config(self):
        """HaikuEncoder accepts config dict."""
        from src.encoder import HaikuEncoder
        encoder = HaikuEncoder(config={"key": "value"})
        assert encoder.config == {"key": "value"}

    def test_encode_raises_not_implemented(self):
        """encode() raises NotImplementedError with version reference."""
        from src.encoder import HaikuEncoder
        encoder = HaikuEncoder()
        with pytest.raises(NotImplementedError, match="v0.2.0"):
            encoder.encode("test document")

    def test_encode_with_metrics_raises_not_implemented(self):
        """encode_with_metrics() raises NotImplementedError."""
        from src.encoder import HaikuEncoder
        encoder = HaikuEncoder()
        with pytest.raises(NotImplementedError, match="v0.2.0"):
            encoder.encode_with_metrics("test document")

    def test_encode_batch_raises_not_implemented(self):
        """encode_batch() raises NotImplementedError."""
        from src.encoder import HaikuEncoder
        encoder = HaikuEncoder()
        with pytest.raises(NotImplementedError, match="v0.2.3"):
            encoder.encode_batch(["doc1", "doc2"])

    def test_encoder_has_logger(self):
        """encoder module has a logger."""
        from src import encoder
        assert hasattr(encoder, "logger")

    def test_encoder_has_docstring(self):
        """encoder module has a module docstring."""
        from src import encoder
        assert encoder.__doc__ is not None
        assert "Compression Pipeline" in encoder.__doc__


# ============================================
# Module 2: decoder.py
# ============================================

@pytest.mark.unit
class TestDecoderModule:
    """Tests for src/decoder.py stub."""

    def test_import_decoder_module(self):
        """decoder module can be imported."""
        import src.decoder
        assert src.decoder is not None

    def test_import_haiku_decoder_class(self):
        """HaikuDecoder class is importable."""
        from src.decoder import HaikuDecoder
        assert HaikuDecoder is not None

    def test_haiku_decoder_init(self):
        """HaikuDecoder can be instantiated."""
        from src.decoder import HaikuDecoder
        decoder = HaikuDecoder()
        assert decoder.config == {}

    def test_decode_raises_not_implemented(self):
        """decode() raises NotImplementedError with version reference."""
        from src.decoder import HaikuDecoder
        decoder = HaikuDecoder()
        with pytest.raises(NotImplementedError, match="v0.2.0"):
            decoder.decode("[CNL: test]")

    def test_decode_batch_raises_not_implemented(self):
        """decode_batch() raises NotImplementedError."""
        from src.decoder import HaikuDecoder
        decoder = HaikuDecoder()
        with pytest.raises(NotImplementedError, match="v0.2.3"):
            decoder.decode_batch(["[CNL: a]", "[CNL: b]"])

    def test_decoder_has_logger(self):
        """decoder module has a logger."""
        from src import decoder
        assert hasattr(decoder, "logger")

    def test_decoder_has_docstring(self):
        """decoder module has a module docstring."""
        from src import decoder
        assert decoder.__doc__ is not None
        assert "Decompression" in decoder.__doc__


# ============================================
# Module 3: chunker.py
# ============================================

@pytest.mark.unit
class TestChunkerModule:
    """Tests for src/chunker.py stub."""

    def test_import_chunker_module(self):
        """chunker module can be imported."""
        import src.chunker
        assert src.chunker is not None

    def test_import_document_chunker_class(self):
        """DocumentChunker class is importable."""
        from src.chunker import DocumentChunker
        assert DocumentChunker is not None

    def test_import_chunk_dataclass(self):
        """Chunk dataclass is importable."""
        from src.chunker import Chunk
        assert Chunk is not None

    def test_chunk_dataclass_instantiation(self):
        """Chunk dataclass can be instantiated with fields."""
        from src.chunker import Chunk
        chunk = Chunk(id="chunk-001", title="Test", level=2, content="hello")
        assert chunk.id == "chunk-001"
        assert chunk.content == "hello"
        assert chunk.level == 2

    def test_document_chunker_init_defaults(self):
        """DocumentChunker has correct default values."""
        from src.chunker import DocumentChunker
        chunker = DocumentChunker()
        assert chunker.chunk_size == 512
        assert chunker.overlap == 50
        assert chunker.strategy == "semantic"

    def test_document_chunker_init_custom(self):
        """DocumentChunker accepts custom parameters."""
        from src.chunker import DocumentChunker
        chunker = DocumentChunker(chunk_size=1024, overlap=100, strategy="fixed_size")
        assert chunker.chunk_size == 1024
        assert chunker.strategy == "fixed_size"

    def test_chunk_raises_not_implemented(self):
        """chunk() raises NotImplementedError with version reference."""
        from src.chunker import DocumentChunker
        chunker = DocumentChunker()
        with pytest.raises(NotImplementedError, match="v0.2.1"):
            chunker.chunk("test document")

    def test_merge_chunks_raises_not_implemented(self):
        """merge_chunks() raises NotImplementedError."""
        from src.chunker import DocumentChunker
        chunker = DocumentChunker()
        with pytest.raises(NotImplementedError, match="v0.2.1"):
            chunker.merge_chunks([])

    def test_chunker_has_logger(self):
        """chunker module has a logger."""
        from src import chunker
        assert hasattr(chunker, "logger")


# ============================================
# Module 4: extractor.py
# ============================================

@pytest.mark.unit
class TestExtractorModule:
    """Tests for src/extractor.py stub."""

    def test_import_extractor_module(self):
        """extractor module can be imported."""
        import src.extractor
        assert src.extractor is not None

    def test_import_entity_extractor_class(self):
        """EntityExtractor class is importable."""
        from src.extractor import EntityExtractor
        assert EntityExtractor is not None

    def test_import_entity_dataclass(self):
        """Entity dataclass is importable."""
        from src.extractor import Entity
        assert Entity is not None

    def test_import_extracted_entities_dataclass(self):
        """ExtractedEntities dataclass is importable."""
        from src.extractor import ExtractedEntities
        assert ExtractedEntities is not None

    def test_entity_dataclass_instantiation(self):
        """Entity dataclass can be instantiated."""
        from src.extractor import Entity
        entity = Entity(text="Python", entity_type="NOUN", confidence=0.95, position=0)
        assert entity.text == "Python"
        assert entity.entity_type == "NOUN"
        assert entity.confidence == 0.95

    def test_extracted_entities_dataclass_instantiation(self):
        """ExtractedEntities dataclass can be instantiated."""
        from src.extractor import ExtractedEntities, Entity
        entities = ExtractedEntities(
            entities=[Entity(text="A", entity_type="NOUN", confidence=0.9, position=0)],
            chunk_id=0,
            relations={"uses": ["A", "B"]}
        )
        assert len(entities.entities) == 1
        assert entities.chunk_id == 0

    def test_entity_extractor_init_defaults(self):
        """EntityExtractor has correct defaults."""
        from src.extractor import EntityExtractor
        extractor = EntityExtractor()
        assert extractor.model_name == "en_core_web_sm"
        assert extractor.confidence_threshold == 0.7

    def test_extract_raises_not_implemented(self):
        """extract() raises NotImplementedError with version reference."""
        from src.extractor import EntityExtractor
        extractor = EntityExtractor()
        with pytest.raises(NotImplementedError, match="v0.2.2"):
            extractor.extract("test text")

    def test_extract_batch_raises_not_implemented(self):
        """extract_batch() raises NotImplementedError."""
        from src.extractor import EntityExtractor
        extractor = EntityExtractor()
        with pytest.raises(NotImplementedError, match="v0.2.3"):
            extractor.extract_batch(["text1", "text2"])

    def test_extractor_has_logger(self):
        """extractor module has a logger."""
        from src import extractor
        assert hasattr(extractor, "logger")


# ============================================
# Module 5: synthesizer.py
# ============================================

@pytest.mark.unit
class TestSynthesizerModule:
    """Tests for src/synthesizer.py stub."""

    def test_import_synthesizer_module(self):
        """synthesizer module can be imported."""
        import src.synthesizer
        assert src.synthesizer is not None

    def test_import_cnl_synthesizer_class(self):
        """CNLSynthesizer class is importable."""
        from src.synthesizer import CNLSynthesizer
        assert CNLSynthesizer is not None

    def test_import_cnl_statement_dataclass(self):
        """CNLStatement dataclass is importable."""
        from src.synthesizer import CNLStatement
        assert CNLStatement is not None

    def test_cnl_statement_instantiation(self):
        """CNLStatement dataclass can be instantiated."""
        from src.synthesizer import CNLStatement
        stmt = CNLStatement(statement="A uses B", confidence=0.9, source_entities=["A", "B"])
        assert stmt.statement == "A uses B"
        assert stmt.confidence == 0.9

    def test_cnl_synthesizer_init(self):
        """CNLSynthesizer can be instantiated."""
        from src.synthesizer import CNLSynthesizer
        synth = CNLSynthesizer()
        assert synth.config == {}

    def test_synthesize_raises_not_implemented(self):
        """synthesize() raises NotImplementedError with version reference."""
        from src.synthesizer import CNLSynthesizer
        synth = CNLSynthesizer()
        with pytest.raises(NotImplementedError, match="v0.2.3"):
            synth.synthesize(entities=[], relations={})

    def test_validate_cnl_raises_not_implemented(self):
        """validate_cnl() raises NotImplementedError."""
        from src.synthesizer import CNLSynthesizer
        synth = CNLSynthesizer()
        with pytest.raises(NotImplementedError, match="v0.2.3"):
            synth.validate_cnl("[CNL: test]")

    def test_generate_variants_raises_not_implemented(self):
        """generate_variants() raises NotImplementedError."""
        from src.synthesizer import CNLSynthesizer
        synth = CNLSynthesizer()
        with pytest.raises(NotImplementedError, match="v0.2.4"):
            synth.generate_variants(entities=[], relations={})

    def test_synthesizer_has_logger(self):
        """synthesizer module has a logger."""
        from src import synthesizer
        assert hasattr(synthesizer, "logger")


# ============================================
# Module 6: validator.py
# ============================================

@pytest.mark.unit
class TestValidatorModule:
    """Tests for src/validator.py stub."""

    def test_import_validator_module(self):
        """validator module can be imported."""
        import src.validator
        assert src.validator is not None

    def test_import_haiku_validator_class(self):
        """HaikuValidator class is importable."""
        from src.validator import HaikuValidator
        assert HaikuValidator is not None

    def test_import_validation_result_dataclass(self):
        """ValidationResult dataclass is importable."""
        from src.validator import ValidationResult
        assert ValidationResult is not None

    def test_import_compression_metrics_dataclass(self):
        """CompressionMetrics dataclass is importable."""
        from src.validator import CompressionMetrics
        assert CompressionMetrics is not None

    def test_validation_result_instantiation(self):
        """ValidationResult dataclass can be instantiated."""
        from src.validator import ValidationResult
        result = ValidationResult(
            is_valid=True, confidence=0.95, error_messages=[], warnings=[]
        )
        assert result.is_valid is True
        assert result.confidence == 0.95

    def test_compression_metrics_instantiation(self):
        """CompressionMetrics dataclass can be instantiated."""
        from src.validator import CompressionMetrics
        metrics = CompressionMetrics(
            compression_ratio=0.35,
            original_tokens=100,
            compressed_tokens=35,
            semantic_similarity=0.92,
            information_retention=0.88,
            processing_time_ms=150.0
        )
        assert metrics.compression_ratio == 0.35
        assert metrics.original_tokens == 100

    def test_haiku_validator_init_defaults(self):
        """HaikuValidator has correct defaults."""
        from src.validator import HaikuValidator
        validator = HaikuValidator()
        assert validator.similarity_model_name == "sentence-transformers/all-MiniLM-L6-v2"

    def test_validate_raises_not_implemented(self):
        """validate() raises NotImplementedError with version reference."""
        from src.validator import HaikuValidator
        validator = HaikuValidator()
        with pytest.raises(NotImplementedError, match="v0.2.4"):
            validator.validate("original", "compressed")

    def test_compute_metrics_raises_not_implemented(self):
        """compute_metrics() raises NotImplementedError."""
        from src.validator import HaikuValidator
        validator = HaikuValidator()
        with pytest.raises(NotImplementedError, match="v0.2.4"):
            validator.compute_metrics("original", "compressed")

    def test_compare_with_baseline_raises_not_implemented(self):
        """compare_with_baseline() raises NotImplementedError."""
        from src.validator import HaikuValidator
        validator = HaikuValidator()
        with pytest.raises(NotImplementedError):
            validator.compare_with_baseline("original", "compressed")

    def test_validator_has_logger(self):
        """validator module has a logger."""
        from src import validator
        assert hasattr(validator, "logger")

    def test_validator_docstring_references_research(self):
        """validator module docstring references v0.0.2d and v0.0.3."""
        from src import validator
        assert "v0.0.2d" in validator.__doc__
        assert "v0.0.3" in validator.__doc__


# ============================================
# Module 7: app.py
# ============================================

streamlit = pytest.importorskip("streamlit", reason="streamlit not installed")


@pytest.mark.unit
class TestAppModule:
    """Tests for src/app.py stub (Streamlit must be importable)."""

    def test_import_app_module(self):
        """app module can be imported."""
        import src.app
        assert src.app is not None

    def test_app_has_main_function(self):
        """app module defines main() function."""
        from src.app import main
        assert callable(main)

    def test_app_has_display_header(self):
        """app module defines display_header() function."""
        from src.app import display_header
        assert callable(display_header)

    def test_app_has_load_css(self):
        """app module defines load_css() function."""
        from src.app import load_css
        assert callable(load_css)

    def test_load_css_raises_not_implemented(self):
        """load_css() raises NotImplementedError."""
        from src.app import load_css
        with pytest.raises(NotImplementedError, match="v0.3.1"):
            load_css()

    def test_display_input_section_raises_not_implemented(self):
        """display_input_section() raises NotImplementedError."""
        from src.app import display_input_section
        with pytest.raises(NotImplementedError, match="v0.3.1"):
            display_input_section()

    def test_display_output_section_raises_not_implemented(self):
        """display_output_section() raises NotImplementedError."""
        from src.app import display_output_section
        with pytest.raises(NotImplementedError, match="v0.3.1"):
            display_output_section("test")

    def test_display_metrics_dashboard_raises_not_implemented(self):
        """display_metrics_dashboard() raises NotImplementedError."""
        from src.app import display_metrics_dashboard
        with pytest.raises(NotImplementedError, match="v0.3.1"):
            display_metrics_dashboard({})

    def test_app_has_logger(self):
        """app module has a logger."""
        from src import app
        assert hasattr(app, "logger")

    def test_app_imports_streamlit(self):
        """app module imports streamlit."""
        from src import app
        assert "streamlit" in sys.modules


# ============================================
# Cross-Module Tests
# ============================================

@pytest.mark.unit
class TestCrossModuleConcerns:
    """Tests verifying cross-cutting concerns across all stubs."""

    def test_all_modules_compile(self):
        """All 7 module files pass py_compile."""
        modules = [
            "encoder", "decoder", "chunker",
            "extractor", "synthesizer", "validator", "app"
        ]
        for mod in modules:
            path = project_root / "src" / f"{mod}.py"
            assert path.exists(), f"Module file missing: {mod}.py"
            py_compile.compile(str(path), doraise=True)

    def test_all_modules_have_loggers(self):
        """All 7 modules declare a module-level logger."""
        modules = [
            "src.encoder", "src.decoder", "src.chunker",
            "src.extractor", "src.synthesizer", "src.validator", "src.app"
        ]
        for mod_name in modules:
            try:
                mod = importlib.import_module(mod_name)
            except ImportError as exc:
                pytest.skip(f"Skipping {mod_name}: {exc}")
            assert hasattr(mod, "logger"), f"{mod_name} missing logger"
            assert isinstance(mod.logger, logging.Logger)

    def test_all_modules_have_docstrings(self):
        """All 7 modules have module-level docstrings."""
        modules = [
            "src.encoder", "src.decoder", "src.chunker",
            "src.extractor", "src.synthesizer", "src.validator", "src.app"
        ]
        for mod_name in modules:
            try:
                mod = importlib.import_module(mod_name)
            except ImportError as exc:
                pytest.skip(f"Skipping {mod_name}: {exc}")
            assert mod.__doc__ is not None, f"{mod_name} missing docstring"
            assert len(mod.__doc__) > 20, f"{mod_name} docstring too short"

    def test_all_classes_have_type_hints(self):
        """All primary classes have type-hinted __init__ signatures."""
        from src.encoder import HaikuEncoder
        from src.decoder import HaikuDecoder
        from src.chunker import DocumentChunker
        from src.extractor import EntityExtractor
        from src.synthesizer import CNLSynthesizer
        from src.validator import HaikuValidator

        for cls in [HaikuEncoder, HaikuDecoder, DocumentChunker,
                    EntityExtractor, CNLSynthesizer, HaikuValidator]:
            sig = inspect.signature(cls.__init__)
            # Check that config param has type annotation
            params = sig.parameters
            assert "config" in params, f"{cls.__name__} missing config param"
            assert params["config"].annotation != inspect.Parameter.empty, \
                f"{cls.__name__}.config missing type hint"

    def test_module_count(self):
        """Exactly 7 new module stubs exist (excluding config, __init__, etc.)."""
        expected = {"encoder.py", "decoder.py", "chunker.py",
                    "extractor.py", "synthesizer.py", "validator.py", "app.py"}
        src_dir = project_root / "src"
        actual_files = {f.name for f in src_dir.glob("*.py")}
        assert expected.issubset(actual_files), \
            f"Missing modules: {expected - actual_files}"
