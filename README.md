# lumiere
Lumière Shopify theme: custom sections, product grids, cart UX, and scalable e-commerce architecture.

## Shopify Themes

This repository contains the Lumière Shopify theme. Use the Shopify CLI to push changes to either a development (unpublished) theme or to an existing live theme.

**Recommended: Push by theme ID to avoid duplicates**

First, list your themes to get the ID:

```bash
shopify theme list
```

Then push to that specific theme:

```bash
shopify theme push --theme <THEME_ID>
```

**Alternative: Push by theme name**

- Create or update an unpublished development theme named "Development":

```bash
shopify theme push --unpublished -t ""
```

- Push to an existing theme by its ID (replace the ID) and publish immediately:

```bash
shopify theme push --themeid=123456789 --publish
```

- To review available flags for your installed CLI:

```bash
shopify theme push --help
```

Notes:
- The `-t` shortcut for specifying a theme name works in this environment (example above).
- If a flag returns an error (for example, `--theme-name`), consult `shopify theme push --help` for the exact flags supported by your CLI version.
- **Important:** Pushing to the same theme name (e.g., `-t "Development"`) updates the existing theme in place - it does NOT create a new theme each time. To create a new theme, use a different name.

### Pulling themes

Pull a remote theme into your local workspace using the Shopify CLI. Examples:

- Pull a theme by name (development):

```bash
shopify theme pull -t "Development"
```

- Pull a theme by ID (replace the ID):

```bash
shopify theme pull --themeid=123456789
```

- To review available flags for `pull` on your installed CLI:

```bash
shopify theme pull --help
```

Note: CLI flags can vary by version — prefer `--help` if a flag returns an error.

### Local development and testing

Develop and preview your theme locally before pushing to Shopify. The Shopify CLI provides a local development server with hot reload.

**Start local development server:**

```bash
shopify theme dev
```

This will:
- Start a local server (typically at `http://127.0.0.1:9292`)
- Sync your local files with a development theme on your store
- Auto-reload changes as you edit files
- Open a preview URL in your browser

**Start with a specific theme:**

```bash
shopify theme dev -t "Development"
```

**Test locally without syncing to store:**

```bash
shopify theme dev --only
```

**Common workflow:**

1. Pull the latest theme from Shopify:
   ```bash
   shopify theme pull -t "Development"
   ```

2. Start local dev server:
   ```bash
   shopify theme dev
   ```

3. Make changes to your theme files (the browser will auto-refresh)

4. Test thoroughly in the local preview

5. Push to development theme for first time:
   ```bash
   shopify theme push --unpublished -t 185011470615
   ```
   . shopify theme push --theme="Development"
   . Push to live theme:
   ```bash
   shopify theme push --unpublished -t "183610474775"
   ```

6. Once verified, merge to main to deploy to live "Radiant" theme

**Useful commands:**

```bash
# Check current theme info
shopify theme info

# List all themes on your store
shopify theme list

# Open theme editor in browser
shopify theme open

# Check CLI version
shopify version
```

## Automated product descriptions

This repository includes a small script to generate product descriptions from a CSV of product titles. The script supports a simple templated mode (no external API) and an optional OpenAI mode for higher-quality descriptions.

Files:
- `scripts/generate_descriptions.py`: main script
- `requirements.txt`: optional dependency (`openai`) for OpenAI mode

Quickstart (templated descriptions):

```bash
python3 scripts/generate_descriptions.py -i products.csv -o products_with_descriptions.csv
```

Use a custom template (use `{title}` as placeholder):

```bash
python3 scripts/generate_descriptions.py -i products.csv -o out.csv --template "{title} — A premium product for modern living."
```

OpenAI mode (requires `OPENAI_API_KEY` env var):

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="sk..."
python3 scripts/generate_descriptions.py -i products.csv -o out.csv --mode openai
```

The script writes a `body_html` column by default. Use `--body-column` to change the output column name.

## Upload products to Shopify

Upload products from a CSV file to your Shopify store using the Admin API. This can be done manually or automatically via GitHub Actions.

### CSV Format

Create a CSV file (e.g., `products.csv`) with the following columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `title` | Yes | Product title | "Cotton T-Shirt" |
| `body_html` | No | Product description (HTML) | "<p>Comfortable cotton tee</p>" |
| `vendor` | No | Product vendor | "Lumière" |
| `product_type` | No | Product type/category | "Apparel" |
| `tags` | No | Comma-separated tags | "summer, casual" |
| `price` | No | Variant price | "29.99" |
| `sku` | No | Variant SKU | "TSHIRT-BLK-M" |
| `inventory_quantity` | No | Stock quantity | "100" |
| `image_src` | No | Product image URL | "https://..." |
| `option1_name` | No | First option name | "Size" |
| `option1_value` | No | First option value | "Medium" |
| `option2_name` | No | Second option name | "Color" |
| `option2_value` | No | Second option value | "Black" |
| `option3_name` | No | Third option name | "Material" |
| `option3_value` | No | Third option value | "Cotton" |

Example CSV:
```csv
title,body_html,vendor,product_type,price,sku,inventory_quantity,tags,image_src
"Cotton T-Shirt","<p>Soft and comfortable</p>","Lumière","Apparel","29.99","TSHIRT-001","50","summer,casual","https://example.com/image.jpg"
```

### Manual Upload

Install dependencies and run the script:

```bash
pip install -r requirements.txt
export SHOPIFY_STORE="your-store.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="shpat_..."
python3 scripts/upload_products.py -i products.csv
```

Test without uploading (dry run):

```bash
python3 scripts/upload_products.py -i products.csv --dry-run
```

### Automatic Upload via GitHub Actions

The workflow `.github/workflows/upload-products.yml` automatically uploads products when:
- You push a `products.csv` or `data/products.csv` file to the `main` branch
- You manually trigger the workflow

**Setup:**

1. Create a Shopify Admin API access token:
   - Go to your Shopify admin → Settings → Apps and sales channels → Develop apps
   - Create a custom app with `write_products` permission
   - Copy the Admin API access token

2. Add repository secrets (Settings → Secrets and variables → Actions):
   - `SHOPIFY_STORE`: Your store domain (e.g., `example-store.myshopify.com`)
   - `SHOPIFY_ACCESS_TOKEN`: Your Admin API access token (starts with `shpat_`)

3. Commit and push your `products.csv` file to trigger the workflow

**Manual trigger:**

You can also manually run the workflow from the Actions tab and specify a custom CSV file path.

## Continuous deploy (GitHub Actions)

A workflow is included to deploy the theme when changes are pushed to any branch.

**Branch-based deployment:**
- `main` branch → Pushes to **Radiant** (live theme)
- All other branches → Push to **Development** (unpublished theme)

Required repository secrets:
- `SHOPIFY_STORE` — your store domain (example: `example-store.myshopify.com`)
- `SHOPIFY_PASSWORD` — a token or password that your CLI can use for non-interactive authentication

The workflow file: `.github/workflows/deploy-theme.yml`

Notes:
- GitHub Actions runners need a non-interactive way to authenticate. Configure the required secrets in your repository settings before enabling the workflow.
- If your Shopify CLI version uses different flags for login or push, update `.github/workflows/deploy-theme.yml` accordingly.
- The main branch deploys directly to your live "Radiant" theme, so test changes in feature branches first.
