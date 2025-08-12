# Font Setup Instructions

## Required Font Files

To complete the font setup, you need to add the NCL BasefighDemo font files to this directory:

### NCL BasefighDemo Font
- `NCL-BasefighDemo.woff2` (Web Open Font Format 2.0 - recommended)
- `NCL-BasefighDemo.woff` (Web Open Font Format - fallback)
- `NCL-BasefighDemo.ttf` (TrueType Font - fallback)

## Font Usage

- **NCL BasefighDemo**: Used for logos, headings, and titles
- **IM Fell English**: Used for body text, links, and general content (loaded from Google Fonts)

## How to Add Font Files

1. Obtain the NCL BasefighDemo font files from your font provider
2. Place the font files in this directory (`public/fonts/`)
3. Ensure the filenames match exactly:
   - `NCL-BasefighDemo.woff2`
   - `NCL-BasefighDemo.woff`
   - `NCL-BasefighDemo.ttf`

## Font Loading

The fonts are automatically loaded via CSS in `src/index.css`:
- IM Fell English is loaded from Google Fonts
- NCL BasefighDemo is loaded from local files using `@font-face`

## Fallback Fonts

If the custom fonts fail to load, the system will fall back to:
- Serif fonts for both NCL BasefighDemo and IM Fell English

## Testing

After adding the font files, restart your development server and check that:
1. The logo and headings use NCL BasefighDemo
2. Body text and links use IM Fell English
3. Fonts load properly without fallback to system fonts 