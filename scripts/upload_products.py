#!/usr/bin/env python3
"""Upload products to Shopify from a CSV file using the Admin API.

Usage:
  python scripts/upload_products.py -i products.csv

Required environment variables:
  SHOPIFY_STORE: Your store domain (e.g., example-store.myshopify.com)
  SHOPIFY_ACCESS_TOKEN: Admin API access token with product write permissions
"""
import argparse
import csv
import os
import sys
import requests
from typing import Dict, List, Optional


def parse_csv(file_path: str) -> List[Dict[str, str]]:
    """Read CSV file and return list of product dictionaries."""
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def create_product_payload(row: Dict[str, str]) -> Dict:
    """Convert CSV row to Shopify product payload."""
    # Basic product structure
    product = {
        "title": row.get("title", "").strip(),
        "body_html": row.get("body_html", "").strip(),
        "vendor": row.get("vendor", "").strip(),
        "product_type": row.get("product_type", "").strip(),
        "tags": row.get("tags", "").strip(),
    }
    
    # Handle variants
    variants = []
    variant = {
        "price": row.get("price", "0.00"),
        "sku": row.get("sku", "").strip(),
        "inventory_quantity": int(row.get("inventory_quantity", "0")),
    }
    
    # Add variant option fields if present
    if row.get("option1_value"):
        variant["option1"] = row.get("option1_value", "").strip()
    if row.get("option2_value"):
        variant["option2"] = row.get("option2_value", "").strip()
    if row.get("option3_value"):
        variant["option3"] = row.get("option3_value", "").strip()
    
    variants.append(variant)
    product["variants"] = variants
    
    # Handle product options
    options = []
    if row.get("option1_name"):
        options.append({
            "name": row.get("option1_name", "").strip(),
            "values": [row.get("option1_value", "").strip()] if row.get("option1_value") else []
        })
    if row.get("option2_name"):
        options.append({
            "name": row.get("option2_name", "").strip(),
            "values": [row.get("option2_value", "").strip()] if row.get("option2_value") else []
        })
    if row.get("option3_name"):
        options.append({
            "name": row.get("option3_name", "").strip(),
            "values": [row.get("option3_value", "").strip()] if row.get("option3_value") else []
        })
    
    if options:
        product["options"] = options
    
    # Handle images
    if row.get("image_src"):
        product["images"] = [{"src": row.get("image_src", "").strip()}]
    
    # Remove empty fields
    product = {k: v for k, v in product.items() if v}
    
    return {"product": product}


def upload_product(store: str, access_token: str, product_data: Dict) -> Dict:
    """Upload a single product to Shopify."""
    url = f"https://{store}/admin/api/2024-01/products.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": access_token
    }
    
    response = requests.post(url, json=product_data, headers=headers)
    
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Failed to create product: {response.status_code} - {response.text}")


def main():
    parser = argparse.ArgumentParser(description="Upload products to Shopify from CSV")
    parser.add_argument("-i", "--input", required=True, help="Input CSV file path")
    parser.add_argument("--dry-run", action="store_true", help="Print payloads without uploading")
    args = parser.parse_args()
    
    # Get credentials from environment
    store = os.environ.get("SHOPIFY_STORE")
    access_token = os.environ.get("SHOPIFY_ACCESS_TOKEN")
    
    if not args.dry_run and (not store or not access_token):
        print("Error: SHOPIFY_STORE and SHOPIFY_ACCESS_TOKEN environment variables required")
        sys.exit(1)
    
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}")
        sys.exit(2)
    
    # Parse CSV
    rows = parse_csv(args.input)
    print(f"Found {len(rows)} products in CSV")
    
    # Process each product
    success_count = 0
    error_count = 0
    
    for idx, row in enumerate(rows, 1):
        title = row.get("title", "").strip()
        if not title:
            print(f"Row {idx}: Skipping - no title")
            continue
        
        try:
            payload = create_product_payload(row)
            
            if args.dry_run:
                print(f"Row {idx}: {title}")
                print(f"  Payload: {payload}")
            else:
                result = upload_product(store, access_token, payload)
                product_id = result.get("product", {}).get("id")
                print(f"Row {idx}: ✓ Created product '{title}' (ID: {product_id})")
                success_count += 1
        except Exception as e:
            print(f"Row {idx}: ✗ Error creating '{title}': {e}")
            error_count += 1
    
    print(f"\nCompleted: {success_count} successful, {error_count} errors")
    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
