"""
Registry of libraries supported in CrewAI-Studio environment

This module contains the complete list of libraries available in the CrewAI-Studio
environment for custom component generation. Any dependency requested in a tool
specification will be validated against this registry.

Source: CrewAI-Studio\requirements.txt
Last Updated: 2025-12-11
Total Libraries: 253
CrewAI Version: 1.5.0
"""

from typing import Dict, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PYTHON STANDARD LIBRARY (Always Available - No Installation Required)
# ============================================================================
STDLIB_MODULES = {
    # Core modules
    "typing", "types", "sys", "os", "io", "builtins",

    # Text processing
    "re", "string", "textwrap", "unicodedata", "stringprep",

    # Data structures
    "collections", "array", "heapq", "bisect", "weakref",
    "copy", "pprint", "reprlib", "enum",

    # Numbers and math
    "math", "cmath", "decimal", "fractions", "random", "statistics",

    # Functional programming
    "itertools", "functools", "operator",

    # File and directory
    "pathlib", "os.path", "fileinput", "stat", "filecmp",
    "tempfile", "glob", "fnmatch", "shutil",

    # Data persistence
    "pickle", "shelve", "dbm", "sqlite3",

    # Data compression
    "zlib", "gzip", "bz2", "lzma", "zipfile", "tarfile",

    # File formats
    "csv", "configparser", "json", "xml", "html",

    # Networking
    "urllib", "urllib.request", "urllib.parse", "urllib.error",
    "http", "http.client", "http.server", "socketserver",
    "socket", "ssl",

    # Email
    "email", "smtplib", "poplib", "imaplib",

    # Date and time
    "datetime", "time", "calendar", "zoneinfo",

    # Concurrency
    "threading", "multiprocessing", "concurrent", "subprocess",
    "queue", "asyncio",

    # Context variables
    "contextvars",

    # Cryptography
    "hashlib", "hmac", "secrets",

    # OS interfaces
    "getpass", "curses", "platform", "errno", "ctypes",

    # Debugging
    "logging", "warnings", "pdb", "trace", "traceback",

    # Python runtime
    "dataclasses", "abc", "atexit", "traceback", "gc",
    "inspect", "importlib",

    # Code parsing
    "ast", "symtable", "token", "keyword", "tokenize",
    "dis", "pickletools",
}


# ============================================================================
# CREWAI SUPPORTED LIBRARIES (From CrewAI-Studio requirements.txt)
# ============================================================================
SUPPORTED_LIBRARIES = {
    # ========================================
    # CORE CREWAI
    # ========================================
    "accelerate": "1.12.0",
    "crewai": "1.5.0",
    "crewai-tools": "1.5.0",

    # ========================================
    # AI & LLM LIBRARIES
    # ========================================
    "anthropic": "0.75.0",
    "openai": "2.8.1",
    "groq": "0.36.0",
    "litellm": "1.80.5",
    "ollama": "0.6.1",

    # ========================================
    # LANGCHAIN ECOSYSTEM
    # ========================================
    "langchain": "1.1.0",
    "langchain-classic": "1.0.0",
    "langchain-community": "0.4.1",
    "langchain-core": "1.1.0",
    "langchain-groq": "1.1.0",
    "langchain-ollama": "1.0.0",
    "langchain-openai": "1.1.0",
    "langchain-text-splitters": "1.0.0",
    "langchain-anthropic": "1.2.0",
    "langgraph": "1.0.3",
    "langgraph-checkpoint": "3.0.1",
    "langgraph-prebuilt": "1.0.5",
    "langgraph-sdk": "0.2.10",
    "langsmith": "0.4.47",

    # ========================================
    # DATA PROCESSING
    # ========================================
    "pandas": "2.3.3",
    "numpy": "2.2.6",
    "scipy": "1.16.3",
    "openpyxl": "3.1.5",
    "xlsxwriter": "3.2.9",
    "et_xmlfile": "2.0.0",
    "narwhals": "2.12.0",
    "pyarrow": "21.0.0",

    # ========================================
    # HTTP & WEB LIBRARIES
    # ========================================
    "requests": "2.32.5",
    "requests-oauthlib": "2.0.0",
    "requests-toolbelt": "1.0.0",
    "httpx": "0.28.1",
    "httpx-sse": "0.4.3",
    "httpcore": "1.0.9",
    "httptools": "0.7.1",
    "aiohttp": "3.13.2",
    "aiohappyeyeballs": "2.6.1",
    "aiosignal": "1.4.0",
    "h11": "0.16.0",
    "primp": "0.15.0",

    # ========================================
    # HTML & WEB SCRAPING
    # ========================================
    "beautifulsoup4": "4.14.2",
    "soupsieve": "2.8",
    "lxml": "6.0.2",

    # ========================================
    # DOCUMENT PROCESSING
    # ========================================
    "pypdf": "6.4.0",
    "pdfplumber": "0.11.8",
    "pdfminer.six": "20251107",
    "python-docx": "1.2.0",
    "python-pptx": "1.0.2",
    "docling": "2.63.0",
    "docling-core": "2.52.0",
    "docling-ibm-models": "3.10.2",
    "docling-parse": "4.7.1",
    "pypdfium2": "4.30.0",
    "openpyxl": "3.1.5",

    # ========================================
    # VECTOR DATABASES & EMBEDDINGS
    # ========================================
    "chromadb": "1.1.1",
    "lancedb": "0.25.3",
    "lance-namespace": "0.0.21",
    "lance-namespace-urllib3-client": "0.0.21",
    "pylance": "0.39.0",

    # ========================================
    # DATABASE LIBRARIES
    # ========================================
    "sqlalchemy": "2.0.44",
    "psycopg2-binary": "2.9.11",
    "snowflake-connector-python": "4.1.0",

    # ========================================
    # VALIDATION & SERIALIZATION
    # ========================================
    "pydantic": "2.12.4",
    "pydantic-settings": "2.12.0",
    "pydantic_core": "2.41.5",
    "pyyaml": "6.0.3",
    "python-dotenv": "1.2.1",
    "toml": "0.10.2",
    "tomli": "2.3.0",
    "tomli_w": "1.2.0",
    "tomlkit": "0.13.3",

    # ========================================
    # JSON & DATA FORMATS
    # ========================================
    "json5": "0.12.1",
    "json_repair": "0.25.2",
    "jsonlines": "4.0.0",
    "jsonpatch": "1.33",
    "jsonpointer": "3.0.0",
    "jsonref": "1.1.0",
    "jsonschema": "4.25.1",
    "jsonschema-specifications": "2025.9.1",
    "orjson": "3.11.4",
    "ormsgpack": "1.12.0",

    # ========================================
    # STREAMING & API
    # ========================================
    "streamlit": "1.51.0",
    "starlette": "0.50.0",
    "sse-starlette": "3.0.3",
    "uvicorn": "0.38.0",
    "fastapi": "Derived",  # Not in requirements but commonly used

    # ========================================
    # SEARCH LIBRARIES
    # ========================================
    "duckduckgo-search": "8.1.1",

    # ========================================
    # IMAGE & VISION
    # ========================================
    "pillow": "11.3.0",
    "opencv-python": "4.12.0.88",

    # ========================================
    # VIDEO PROCESSING
    # ========================================
    "pytube": "15.0.0",
    "youtube-transcript-api": "1.2.3",

    # ========================================
    # CLOUD & AWS
    # ========================================
    "boto3": "1.41.3",
    "botocore": "1.41.3",
    "s3transfer": "0.15.0",

    # ========================================
    # CONTAINER & EXECUTION
    # ========================================
    "docker": "7.1.0",
    "kubernetes": "34.1.0",

    # ========================================
    # UTILITIES
    # ========================================
    "python-dateutil": "2.9.0.post0",
    "pytz": "2025.2",
    "tzdata": "2025.2",
    "regex": "2025.11.3",
    "Markdown": "3.10",
    "markdown-it-py": "4.0.0",
    "marko": "2.2.1",
    "MarkupSafe": "3.0.3",
    "Faker": "38.2.0",

    # ========================================
    # LOGGING & DEBUGGING
    # ========================================
    "colorama": "0.4.6",
    "coloredlogs": "15.0.1",
    "colorlog": "6.10.1",
    "rich": "14.2.0",
    "Pygments": "2.19.2",

    # ========================================
    # TYPING & VALIDATION
    # ========================================
    "typing_extensions": "4.15.0",
    "typing-inspect": "0.9.0",
    "typing-inspection": "0.4.2",
    "mypy_extensions": "1.1.0",
    "annotated-types": "0.7.0",

    # ========================================
    # ASYNC & CONCURRENCY
    # ========================================
    "anyio": "4.11.0",
    "sniffio": "1.3.1",
    "greenlet": "3.2.4",

    # ========================================
    # SECURITY & CRYPTO
    # ========================================
    "cryptography": "46.0.3",
    "bcrypt": "5.0.0",
    "asn1crypto": "1.5.1",
    "pyOpenSSL": "25.3.0",
    "PyJWT": "2.10.1",
    "oauthlib": "3.3.1",

    # ========================================
    # PARSING & PROCESSING
    # ========================================
    "antlr4-python3-runtime": "4.9.3",
    "docstring_parser": "0.17.0",
    "tree-sitter": "0.25.2",
    "tree-sitter-c": "0.24.1",
    "tree-sitter-java": "0.23.5",
    "tree-sitter-javascript": "0.25.0",
    "tree-sitter-python": "0.25.0",
    "tree-sitter-typescript": "0.23.2",

    # ========================================
    # ML & AI TOOLS
    # ========================================
    "torch": "2.9.1",
    "torchvision": "0.24.1",
    "transformers": "4.57.2",
    "tokenizers": "0.22.1",
    "safetensors": "0.7.0",
    "huggingface-hub": "0.36.0",
    "accelerate": "1.12.0",
    "onnxruntime": "1.23.2",
    "tiktoken": "0.12.0",

    # ========================================
    # NETWORKING
    # ========================================
    "urllib3": "2.3.0",
    "certifi": "2025.11.12",
    "charset-normalizer": "3.4.4",
    "idna": "3.11",
    "websocket-client": "1.9.0",
    "websockets": "15.0.1",

    # ========================================
    # CACHING & STORAGE
    # ========================================
    "cachetools": "6.2.2",
    "diskcache": "5.6.3",

    # ========================================
    # SYSTEM & OS
    # ========================================
    "psutil": "7.1.3",
    "watchdog": "6.0.0",
    "watchfiles": "1.1.1",
    "platformdirs": "4.5.0",
    "appdirs": "1.4.4",

    # ========================================
    # PROGRESS & UI
    # ========================================
    "tqdm": "4.67.1",
    "tabulate": "0.9.0",
    "click": "8.3.1",
    "typer": "0.19.2",
    "shellingham": "1.5.4",

    # ========================================
    # TESTING & QUALITY
    # ========================================
    "pre_commit": "4.5.0",
    "pluggy": "1.6.0",
    "polyfactory": "3.0.0",

    # ========================================
    # BUILD & PACKAGING
    # ========================================
    "build": "1.3.0",
    "setuptools": "80.9.0",
    "packaging": "25.0",
    "pyproject_hooks": "1.2.0",
    "uv": "0.9.11",

    # ========================================
    # PROTOCOLS & SERIALIZATION
    # ========================================
    "protobuf": "6.33.1",
    "googleapis-common-protos": "1.72.0",
    "grpcio": "1.76.0",

    # ========================================
    # TELEMETRY & MONITORING
    # ========================================
    "opentelemetry-api": "1.38.0",
    "opentelemetry-exporter-otlp-proto-common": "1.38.0",
    "opentelemetry-exporter-otlp-proto-grpc": "1.38.0",
    "opentelemetry-exporter-otlp-proto-http": "1.38.0",
    "opentelemetry-proto": "1.38.0",
    "opentelemetry-sdk": "1.38.0",
    "opentelemetry-semantic-conventions": "0.59b0",
    "posthog": "5.4.0",

    # ========================================
    # MISCELLANEOUS
    # ========================================
    "attrs": "25.4.0",
    "backoff": "2.2.1",
    "defusedxml": "0.7.1",
    "deprecation": "2.1.0",
    "dill": "0.4.0",
    "distlib": "0.4.0",
    "distro": "1.9.0",
    "durationpy": "0.10",
    "fastuuid": "0.14.0",
    "filelock": "3.20.0",
    "filetype": "1.2.0",
    "flatbuffers": "25.9.23",
    "frozenlist": "1.8.0",
    "fsspec": "2025.10.0",
    "gitdb": "4.0.12",
    "GitPython": "3.1.45",
    "google-auth": "2.43.0",
    "humanfriendly": "10.0",
    "identify": "2.6.15",
    "importlib_metadata": "8.7.0",
    "importlib_resources": "6.5.2",
    "instructor": "1.13.0",
    "jinja2": "3.1.6",
    "jiter": "0.11.1",
    "jmespath": "1.0.1",
    "latex2mathml": "3.78.1",
    "marshmallow": "3.26.1",
    "mcp": "1.22.0",
    "mdurl": "0.1.2",
    "mmh3": "5.2.0",
    "mpire": "2.10.2",
    "mpmath": "1.3.0",
    "multidict": "6.7.0",
    "multiprocess": "0.70.18",
    "networkx": "3.6",
    "nodeenv": "1.9.1",
    "omegaconf": "2.3.0",
    "overrides": "7.7.0",
    "portalocker": "2.7.0",
    "propcache": "0.4.1",
    "pyasn1": "0.6.1",
    "pyasn1_modules": "0.4.2",
    "pybase64": "1.4.2",
    "pyclipper": "1.3.0.post6",
    "pycparser": "2.23",
    "pydeck": "0.9.1",
    "pylatexenc": "2.10",
    "PyPika": "0.48.9",
    "pyreadline3": "3.5.4",
    "python-multipart": "0.0.20",
    "rapidocr": "3.4.2",
    "referencing": "0.37.0",
    "rpds-py": "0.29.0",
    "rsa": "4.9.1",
    "rtree": "1.4.1",
    "semchunk": "2.2.2",
    "shapely": "2.1.2",
    "six": "1.17.0",
    "smmap": "5.0.2",
    "sortedcontainers": "2.4.0",
    "sympy": "1.14.0",
    "tenacity": "9.1.2",
    "tornado": "6.5.2",
    "ty": "0.0.1a27",
    "virtualenv": "20.35.4",
    "xxhash": "3.6.0",
    "yarl": "1.22.0",
    "zipp": "3.23.0",
    "zstandard": "0.25.0",
    "cffi": "2.0.0",
    "cfgv": "3.5.0",
    "blinker": "1.9.0",
    "altair": "5.5.0",
    "dataclasses-json": "0.6.7",
}


# ============================================================================
# LIBRARY CATEGORIES
# ============================================================================
LIBRARY_CATEGORIES = {
    "stdlib": list(STDLIB_MODULES),
    "crewai": ["crewai", "crewai-tools", "accelerate"],
    "ai_llm": [
        "anthropic", "openai", "groq", "litellm", "ollama",
        "langchain", "langchain-community", "langchain-core",
        "langchain-openai", "langchain-anthropic"
    ],
    "data_processing": ["pandas", "numpy", "scipy", "openpyxl", "xlsxwriter"],
    "web_http": ["requests", "httpx", "aiohttp", "beautifulsoup4", "lxml"],
    "documents": ["pypdf", "pdfplumber", "python-docx", "python-pptx", "docling"],
    "databases": ["chromadb", "lancedb", "sqlalchemy", "psycopg2-binary"],
    "validation": ["pydantic", "pydantic-settings", "pyyaml", "python-dotenv"],
    "search": ["duckduckgo-search"],
    "media": ["pillow", "opencv-python", "pytube"],
    "cloud": ["boto3", "botocore", "docker", "kubernetes"],
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def is_stdlib(library_name: str) -> bool:
    """Check if library is part of Python standard library"""
    # Handle submodules (e.g., urllib.request)
    base_module = library_name.split('.')[0]
    return base_module in STDLIB_MODULES


def is_supported(library_name: str) -> bool:
    """
    Check if library is supported in CrewAI-Studio environment

    Args:
        library_name: Name of the library to check

    Returns:
        True if library is supported (either stdlib or in SUPPORTED_LIBRARIES)
    """
    # Check stdlib first
    if is_stdlib(library_name):
        return True

    # Check supported libraries (case-insensitive)
    library_lower = library_name.lower()
    for lib in SUPPORTED_LIBRARIES:
        if lib.lower() == library_lower:
            return True

    return False


def get_supported_libraries() -> Set[str]:
    """Get set of all supported libraries"""
    return STDLIB_MODULES | set(SUPPORTED_LIBRARIES.keys())


def get_category(library_name: str) -> Optional[str]:
    """Get category of a supported library"""
    for category, libs in LIBRARY_CATEGORIES.items():
        if library_name in libs:
            return category
    return None


def get_alternatives(library_name: str) -> List[str]:
    """
    Suggest alternatives for unsupported library

    Args:
        library_name: Name of the unsupported library

    Returns:
        List of suggested alternatives
    """
    ALTERNATIVES_MAP = {
        # HTTP alternatives
        "urllib2": ["urllib.request (stdlib)", "requests"],
        "urllib3": ["urllib.request (stdlib)", "httpx"],

        # Data processing alternatives
        "polars": ["pandas"],

        # JSON alternatives
        "simplejson": ["json (stdlib)", "orjson"],
        "ujson": ["json (stdlib)", "orjson"],

        # Date/time alternatives
        "arrow": ["datetime (stdlib)", "python-dateutil"],
        "pendulum": ["datetime (stdlib)", "python-dateutil"],

        # Web scraping alternatives
        "scrapy": ["beautifulsoup4", "lxml"],

        # Database alternatives
        "pymongo": ["Use REST API with requests"],
        "redis": ["Use REST API with requests"],

        # Default fallback
        "default": ["Implement manually using Python stdlib"]
    }

    alternatives = ALTERNATIVES_MAP.get(library_name.lower(), ALTERNATIVES_MAP["default"])

    # Add category-based suggestions
    if "http" in library_name.lower() or "web" in library_name.lower():
        alternatives = ["requests", "httpx", "urllib.request (stdlib)"]
    elif "json" in library_name.lower():
        alternatives = ["json (stdlib)", "orjson"]
    elif "csv" in library_name.lower():
        alternatives = ["csv (stdlib)", "pandas"]

    return alternatives


def validate_dependencies(dependencies: List[str]) -> Dict[str, any]:
    """
    Validate list of dependencies

    Args:
        dependencies: List of dependency names

    Returns:
        Dictionary with validation results:
        {
            "all_supported": bool,
            "supported": list,
            "unsupported": list,
            "stdlib": list,
            "external": list,
            "alternatives": dict
        }
    """
    supported = []
    unsupported = []
    stdlib = []
    external = []
    alternatives = {}

    for dep in dependencies:
        if is_stdlib(dep):
            supported.append(dep)
            stdlib.append(dep)
        elif is_supported(dep):
            supported.append(dep)
            external.append(dep)
        else:
            unsupported.append(dep)
            alternatives[dep] = get_alternatives(dep)

    return {
        "all_supported": len(unsupported) == 0,
        "supported": supported,
        "unsupported": unsupported,
        "stdlib": stdlib,
        "external": external,
        "alternatives": alternatives,
        "total": len(dependencies),
        "supported_count": len(supported),
        "unsupported_count": len(unsupported)
    }


# ============================================================================
# LOGGING
# ============================================================================

def log_validation_result(result: Dict[str, any]) -> None:
    """Log validation result for debugging"""
    logger.info(f"Dependency validation: {result['supported_count']}/{result['total']} supported")

    if result['unsupported']:
        logger.warning(f"Unsupported dependencies: {', '.join(result['unsupported'])}")
        for dep, alts in result['alternatives'].items():
            logger.info(f"  {dep} → Alternatives: {', '.join(alts)}")
