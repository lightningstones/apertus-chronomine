# Contributing to ChronoMine AI

Thank you for your interest in contributing to **ChronoMine AI (SwissTunnelCopilot)**! This project is an open-source subterranean situation awareness and compliance copilot powered by the **Apertus v1.5** model family for Hack Apertus 2026.

---

## 📜 Code of Conduct & Open Source Values

We are committed to providing a welcoming, inclusive, and harassment-free experience for everyone. All participants are expected to adhere to standard open-source citizenship, respecting civil engineering safety rigor and sovereign AI data privacy standards.

---

## 🛠️ Development Setup

### 1. Prerequisites
- **Python 3.11+**
- **Docker & Docker Compose** (for containerized execution)
- **Make** (standard build tool)
- **Git**

### 2. Getting Started
```bash
# Clone the repository
git clone https://github.com/lightningstones/apertus-chronomine.git
cd apertus-chronomine

# Create and activate virtual environment
cd track_2b
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies including dev & test tools
pip install -r requirements.txt

# Configure your environment
cp .env.example .env
```

### 3. Running Locally
```bash
# From repository root or track_2b/:
make dev
```
The application will be live at `http://localhost:8000`.

---

## 🧪 Testing & Quality Assurance

We enforce test-driven rigor. Every pull request must pass the automated test suite before merging:

```bash
# Run tests from repository root
make test

# Or directly with pytest
pytest track_2b/tests/ -v
```

### Sovereign Air-Gapped Mode for Tests
By default, the test suite executes in `APERTUS_PROVIDER=mock_offline` mode so that tests can be verified locally and in CI without exposing or requiring external network keys.

---

## 📐 Coding Conventions

- **Python Style**: PEP 8 standards with type hints across all backend models and providers (`pydantic.BaseModel`).
- **Commits**: We follow the **Conventional Commits** specification:
  - `feat(scope): ...` for new features
  - `fix(scope): ...` for bug fixes
  - `docs(scope): ...` for documentation improvements
  - `test(scope): ...` for adding or modifying tests
  - `refactor(scope): ...` for code refactoring
- **Co-Author Attribution**: If pair programming with AI agents or human contributors, use standard Git trailers:
  ```
  Co-authored-by: Name <email>
  ```

---

## 🚢 Pull Request Process

1. **Fork or branch**: Create a feature branch (`git checkout -b feat/my-enhancement`).
2. **Implement & test**: Write clean code, update schemas in `src/backend/models.py`, and add matching tests in `tests/test_api.py`.
3. **Verify green build**: Run `make test` and ensure all tests pass.
4. **Submit PR**: Open a Pull Request targeting the `main` branch with a clear description of changes.

---

## ⚖️ License

By contributing to ChronoMine AI, you agree that your contributions will be licensed under the project's [Apache-2.0 License](LICENSE).
