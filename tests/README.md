# Test Suite

This directory contains unit tests for the memory buffers application.

## Running Tests

### Install Test Dependencies

First, make sure you have the test dependencies installed:

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run Specific Test Files

```bash
# Run tests for a specific module
pytest tests/test_fifo_memory.py

# Run tests for a specific test class
pytest tests/test_fifo_memory.py::TestFIFOMemory

# Run a specific test
pytest tests/test_fifo_memory.py::TestFIFOMemory::test_add_message
```

### Run Tests Verbosely

```bash
pytest -v
```

### Run Tests with Output

```bash
pytest -s
```

## Test Structure

- `test_base.py` - Tests for base memory class and models
- `test_fifo_memory.py` - Tests for FIFO memory implementation
- `test_priority_memory.py` - Tests for Priority memory implementation
- `test_hybrid_memory.py` - Tests for Hybrid memory implementation
- `test_token_counter.py` - Tests for token counting utility
- `test_provider.py` - Tests for LLM provider
- `test_embeddings.py` - Tests for embeddings utility
- `test_settings.py` - Tests for configuration settings
- `conftest.py` - Pytest fixtures and configuration

## Test Coverage

The test suite aims to cover:
- ✅ Memory buffer implementations (FIFO, Priority, Hybrid)
- ✅ Base memory interface
- ✅ Token counting utilities
- ✅ LLM provider abstraction
- ✅ Embedding utilities
- ✅ Configuration settings

## Notes

- Some tests use mocking to avoid requiring actual LLM or embedding services
- Tests are designed to run independently without external dependencies
- Priority memory tests may skip some functionality if ChromaDB or sentence-transformers are unavailable

## Documentation

For detailed documentation on the codebase, see the [Help System](../docs/help/index.html) or [HELP_SYSTEM.md](../HELP_SYSTEM.md).