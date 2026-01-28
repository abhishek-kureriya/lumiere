#!/usr/bin/env python3
"""Generate product descriptions from titles in a CSV file.

Usage:
  python scripts/generate_descriptions.py -i products.csv -o products_out.csv

Modes:
  template: simple templated HTML description (default)
  openai: use OpenAI API to generate descriptions (requires OPENAI_API_KEY)
"""
import argparse
import csv
import os
import sys

try:
    import openai
except Exception:
    openai = None


def generate_template(title: str, template: str | None = None) -> str:
    if template:
        return template.replace("{title}", title)
    return (
        f"<h2>{title}</h2>"
        f"\n<p>Introducing the {title} — crafted for quality, style, and lasting performance."
        " Perfect for everyday use or special occasions, this item blends function with beauty.</p>"
        "\n<ul><li>High-quality materials</li><li>Thoughtful design</li><li>Customer-loved</li></ul>"
    )


def generate_openai(title: str, model: str = "gpt-3.5-turbo", max_tokens: int = 200) -> str:
    if openai is None:
        raise RuntimeError(
            "OpenAI client not installed. Install via `pip install openai` or use template mode."
        )
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Please set the OPENAI_API_KEY environment variable.")
    openai.api_key = api_key
    prompt = (
        f"Write a concise product description in HTML for a product titled: \"{title}\". "
        "Keep it to 2 short paragraphs, emphasize benefits, and include 3 short bullet points."
    )
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    return resp["choices"][0]["message"]["content"].strip()


def main():
    parser = argparse.ArgumentParser(description="Generate product descriptions from a CSV of titles.")
    parser.add_argument("-i", "--input", default="products.csv", help="Input CSV file path")
    parser.add_argument("-o", "--output", default="products_with_descriptions.csv", help="Output CSV file path")
    parser.add_argument("--mode", choices=["template", "openai"], default="template", help="Generation mode")
    parser.add_argument("--template", help="Custom template; use {title} as placeholder")
    parser.add_argument("--title-column", default="title", help="CSV column name that contains the product title (case-insensitive)")
    parser.add_argument("--body-column", default="body_html", help="CSV column name to write description into")
    parser.add_argument("--openai-model", default="gpt-3.5-turbo", help="OpenAI model to use when in openai mode")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}")
        sys.exit(2)

    with open(args.input, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("No rows found in input CSV.")
        sys.exit(1)

    # find title column case-insensitive
    header = reader.fieldnames or []
    title_col = None
    for h in header:
        if h.lower() == args.title_column.lower():
            title_col = h
            break
    if title_col is None:
        print(f"Title column '{args.title_column}' not found in CSV header: {header}")
        sys.exit(2)

    # ensure body column exists in header
    out_header = list(header)
    if args.body_column not in out_header:
        out_header.append(args.body_column)

    out_rows = []
    for r in rows:
        title = r.get(title_col, "").strip()
        if not title:
            desc = ""
        else:
            if args.mode == "template":
                desc = generate_template(title, args.template)
            else:
                try:
                    desc = generate_openai(title, model=args.openai_model)
                except Exception as e:
                    print("OpenAI generation failed:", e)
                    print("Falling back to template generation.")
                    desc = generate_template(title, args.template)
        r[args.body_column] = desc
        out_rows.append(r)

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_header)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
