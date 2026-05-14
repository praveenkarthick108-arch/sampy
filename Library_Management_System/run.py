"""
Library Management System — Startup Script
Run with:  python run.py

No Node.js required. The React frontend is served by FastAPI using CDN builds.
Open http://localhost:8000 in your browser after starting.
"""
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(ROOT, "backend")
VENV_PY_WIN = os.path.join(BACKEND, ".venv", "Scripts", "python.exe")
VENV_PY_UNIX = os.path.join(BACKEND, ".venv", "bin", "python")

def get_python():
    if os.path.isfile(VENV_PY_WIN):
        return VENV_PY_WIN
    if os.path.isfile(VENV_PY_UNIX):
        return VENV_PY_UNIX
    return sys.executable

def install_deps():
    py = get_python()
    req = os.path.join(BACKEND, "requirements.txt")
    print("  Checking dependencies…")
    subprocess.run([py, "-m", "pip", "install", "-r", req, "-q"], check=True)

def main():
    print()
    print("=" * 52)
    print("   Library Management System")
    print("=" * 52)
    print()

    # Install deps if needed (silent if already installed)
    try:
        install_deps()
    except subprocess.CalledProcessError:
        print("  Warning: could not install dependencies automatically.")
        print(f"  Run manually: pip install -r backend/requirements.txt")
    print()
    print("  App   ▶  http://localhost:8000")
    print("  Docs  ▶  http://localhost:8000/docs")
    print()
    print("  Press Ctrl+C to stop the server.")
    print()

    py = get_python()
    os.chdir(BACKEND)
    subprocess.run(
        [py, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        check=False,
    )

if __name__ == "__main__":
    main()
