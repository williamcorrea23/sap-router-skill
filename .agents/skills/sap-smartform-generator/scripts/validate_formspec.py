#!/usr/bin/env python3
"""CLI validation utility for FormSpec JSON files."""

import sys
import json
import argparse
from pathlib import Path

# Add package source directory to path
PACKAGE_SRC = Path(__file__).resolve().parent.parent.parent.parent.parent / "packages" / "smartform-ai-generator" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

from smartform_ai.models.formspec import FormSpec
from smartform_ai.validators.formspec_validator import FormSpecValidator


def main():
    parser = argparse.ArgumentParser(description="Validate FormSpec JSON file")
    parser.add_argument("--input", required=True, help="Path to FormSpec JSON file")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found '{args.input}'")
        sys.exit(1)

    try:
        data = json.loads(input_path.read_text(encoding="utf-8"))
        spec = FormSpec.model_validate(data)
        validator = FormSpecValidator()
        res = validator.validate(spec)

        print(json.dumps(res, indent=2))
        sys.exit(0 if res["is_valid"] else 1)
    except Exception as e:
        print(f"Validation failed with exception: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
