---
name: format-post
description: >
  Creates a Jekyll photo blog post from a folder of images for the hyperfocal blog.
  Use this skill whenever the user wants to turn a folder of photos into a blog post,
  says "format a post", "create a post from the images in X", "make a post for slug X",
  or has a folder of images ready and wants a _posts/ file generated. The skill reads
  EXIF data from the images, views each one for alt text, arranges them into a narrative
  layout using landscape/portrait/diptych includes, renames the files to sequential
  numbers in narrative order, and writes the full post file.
---

# format-post

Converts a folder of images into `_posts/YYYY-MM-DD-slug.md` for the hyperfocal Jekyll blog.
Images are renamed to `1.jpg`, `2.jpg`, ... in the narrative order you choose.

## Inputs

The user provides an image folder, typically `assets/images/<slug>/`. Derive the slug from the folder name.

Use today's date (from `currentDate` in your system context) for the post filename — no need to ask the user for it.

Images may be sorted by leading numeric prefix in the filename (`1-foo.jpg`, `3-bar.jpg`, `10-baz.jpg` → 1, 3, 10).

## Step 1 — Extract image metadata

Run the extraction script:

```bash
python3 .claude/skills/format-post/scripts/extract_images.py <image-folder>
```

This returns JSON for each image:
- `file` — filename
- `orientation` — `"landscape"` or `"portrait"` (based on pixel dimensions)
- `camera` — normalized camera name, e.g. `Leica M11-P`
- `lens` — normalized lens name (see **Lens names** below)
- `lens_raw` — raw EXIF lens string, useful for debugging
- `focal_length`, `shutter`, `aperture`, `iso`, `date`
- `gps` — `{lat, lon}` decimal degrees, or `null`

## Step 2 — View each image

Use the Read tool to view each image file. Write a concise, literal alt tag for each — describe what is visible in the scene, not artistic intent. One sentence.

## Step 3 — Identify the location

If the images have GPS data, identify the specific location from the coordinates using your world geography knowledge. All images from one shoot are typically in the same place. If GPS is absent, ask the user.

Be precise — use the actual place where the photos were taken, not a nearby landmark or transit point. For example, if coordinates fall on an offshore island, name the island rather than the mainland ferry terminal. If in doubt between two candidate names, pick the more specific one.

## Step 4 — Arrange the narrative

Decide on the layout for each image:
- **landscape** → `{% include landscape.html %}`
- **portrait alone** → `{% include portrait.html %}`
- **portrait pair** → `{% include diptych.html %}` (two portraits side by side)

Diptych pairing rules:
- Only pair two portrait-orientation images.
- Pair images that are visually or thematically related.
- A lone portrait is fine — don't force pairings.
- Think about visual rhythm: alternating landscape/diptych/portrait reads well.

## Step 5 — Rename image files

Rename each image to a short descriptive slug based on its subject — for example `stage.jpg`, `captain.jpg`, `candle.jpg`. Slugs should be:
- Lowercase, hyphen-separated, no spaces
- 1–3 words, specific enough to identify the image at a glance
- Unique within the folder (append `-2`, `-3` etc. if two images share a subject, e.g. `candle-1.jpg`, `candle-2.jpg`)

Do **not** use sequential numbers (`1.jpg`, `2.jpg`). The filenames should be opaque to capture order and total count.

To avoid conflicts if a target name already exists as a source name, use a two-phase rename:

```bash
# Phase 1: rename everything to temporary names
mv "<folder>/original.jpg" "<folder>/_tmp_slug.jpg"
# ... one mv per image

# Phase 2: rename temps to final slugs
mv "<folder>/_tmp_slug.jpg" "<folder>/slug.jpg"
# ... one mv per image
```

After renaming, use the slug filenames everywhere in the post.

## Step 6 — Build the EXIF string

Format the EXIF string for each image from the extracted metadata:

```
{camera}. {lens}. {focal_length}, {shutter} sec, ≈ƒ/{aperture}, ISO {iso}. {date}. {city}, {country}.
```

Example:
```
Leica M11-P. Leica APO-Summicron-M 35 ƒ/2 ASPH. 35 mm, 1/250 sec, ≈ƒ/8, ISO 64. 1 January 2024. Wetzlar, Germany.
```

**Lens names:** The EXIF lens string from Leica M cameras is often unreliable for third-party lenses (e.g. Voigtländer lenses may be recorded as Leica Summicron). The script normalizes common Leica lens patterns, but flag any case where:
- The reported focal length seems inconsistent with the image's field of view, or
- The lens make in EXIF is clearly wrong (e.g. `Leica Camera AG` as make for a Voigtländer)

When uncertain, output a comment in the post like `<!-- TODO: verify lens name -->` next to the exif string.

## Step 7 — Write the post file

Create `_posts/YYYY-MM-DD-<slug>.md`:

```markdown
---
layout: post
title: Post Title
description: 
image: /assets/images/<slug>/<cover-slug>.jpg
author: Timothy Leung
---
```

- Leave `description:` blank — the user will fill it in.
- Derive `title:` from the slug or folder name, title-cased. Confirm with user if unsure.
- **Cover image (`image:`)** must be a **landscape-orientation** image. Choose the single most representative landscape image from the set — the one that best conveys the subject and would work well as a grid thumbnail. If there are no landscape images, use the first portrait.

### Include templates

**Landscape:**
```liquid
{% include landscape.html
   src="/assets/images/<slug>/N.jpg"
   alt="Description."
   exif="..."
%}
```

**Portrait:**
```liquid
{% include portrait.html
   src="/assets/images/<slug>/N.jpg"
   alt="Description."
   exif="..."
%}
```

**Diptych (two portraits):**
```liquid
{% include diptych.html
   src_left="/assets/images/<slug>/N.jpg"
   alt_left="Description of left."
   exif_left="..."
   src_right="/assets/images/<slug>/M.jpg"
   alt_right="Description of right."
   exif_right="..."
%}
```
