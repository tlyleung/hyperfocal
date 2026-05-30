# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies (first time or after Gemfile/package.json changes)
bundle install
npm install

# Local development server (hot-reloads content, but not _config.yml)
bundle exec jekyll serve --livereload

# Production build
JEKYLL_ENV=production bundle exec jekyll build
```

Ruby 3.4.4, Node 22.17.0 (see `.ruby-version` and `.node-version`).

## Architecture

This is a Jekyll 4 photo blog deployed to GitHub Pages via `.github/workflows/main.yml`. The build pipeline is:

1. Jekyll processes Liquid templates and Markdown
2. `jekyll-postcss` runs Tailwind CSS (+ cssnano in production) on `assets/css/main.css`
3. `_plugins/mermaid_renderer.rb` converts fenced ` ```mermaid ``` ` blocks into inline SVGs — renders both `neutral` and `dark` themes, caches results by content hash in `.mermaid-cache/`

### Layouts and Includes

- `_layouts/base.html` — outer shell: `<html>`, sticky header, lightbox dialog, footer
- `_layouts/post.html` — wraps content in `<article>` with a header block (date, title, description)
- `_layouts/posts.html` — homepage grid of post cover images with hover reveal

Three photo layout includes used inside post Markdown:

| Include | Parameters | Use for |
|---|---|---|
| `landscape.html` | `src`, `alt`, `exif` | 3:2 landscape image |
| `portrait.html` | `src`, `alt`, `exif` | 2:3 portrait, centered in a 3:2 container |
| `diptych.html` | `src_left/right`, `alt_left/right`, `exif_left/right` | side-by-side portrait pair |

The optional `caption` parameter is separate from `exif`; both are stored as `data-*` attributes and read by the lightbox.

### Lightbox

`assets/js/lightbox.js` drives the full-screen lightbox (`<dialog id="lightbox">` in `base.html`). Images with `cursor-zoom-in` open the lightbox; the Content Credentials link is populated from `data-exif`.

### Styling

Tailwind v3 with `@tailwindcss/typography`. Class source paths are listed in `tailwind.config.js`. Dark mode uses the `dark:` variant. `assets/css/mermaid.css` is injected into Mermaid SVG renders only.

Formatting: `npx prettier --write .` — uses Shopify Liquid + Tailwind prettier plugins (config in `.prettierrc`).

### Sibling Sites

The site is part of a network (`site.sites` in `_config.yml`): *Acta Machina*, *hyperfocal*, *Procedural*. The header dropdown links to the other sites. Each site has its own font configured under `site.sites[title].font`.

## Adding a Post

1. Create `_posts/YYYY-MM-DD-slug.md` with front matter:
   ```yaml
   ---
   layout: post
   title: Post Title
   description: One-paragraph description shown in the post header.
   image: /assets/images/slug/1.jpg  # cover image for the grid
   author: Timothy Leung
   ---
   ```
2. Place images in `assets/images/slug/` — landscape images expected at 2048×1365, portraits at 1365×2048.
3. Compose the body using `{% include landscape.html %}`, `{% include portrait.html %}`, or `{% include diptych.html %}` includes.
