---
name: Growth Intelligence System
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#3c4a43'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#6b7b72'
  outline-variant: '#bacac1'
  surface-tint: '#006c4f'
  primary: '#006c4f'
  on-primary: '#ffffff'
  primary-container: '#00d09c'
  on-primary-container: '#00533c'
  inverse-primary: '#2fe0aa'
  secondary: '#5f5e5e'
  on-secondary: '#ffffff'
  secondary-container: '#e5e2e1'
  on-secondary-container: '#656464'
  tertiary: '#5a5d72'
  on-tertiary: '#ffffff'
  tertiary-container: '#b4b6ce'
  on-tertiary-container: '#44475b'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#59fdc5'
  primary-fixed-dim: '#2fe0aa'
  on-primary-fixed: '#002116'
  on-primary-fixed-variant: '#00513b'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1c1b1b'
  on-secondary-fixed-variant: '#474646'
  tertiary-fixed: '#dfe1fa'
  tertiary-fixed-dim: '#c3c5dd'
  on-tertiary-fixed: '#171a2c'
  on-tertiary-fixed-variant: '#43465a'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  title-lg:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 34px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

The brand personality is rooted in democratic finance: making complex market intelligence feel accessible, transparent, and effortlessly simple. The target audience includes both novice investors and seasoned analysts who value speed and clarity over traditional prestige.

The visual style follows a **Modern Corporate Minimalism** approach. It leverages a "Safe" aesthetic that prioritizes high legibility and a sense of "Air." By utilizing generous whitespace and a singular, vibrant accent color, the UI evokes a feeling of optimism and efficiency. The interface should feel like a lightweight tool that stays out of the user's way, using subtle movement and clean lines to guide the eye toward actionable data.

## Colors

The palette is dominated by **Pure White (#FFFFFF)** to ensure the interface feels open and "breathable." The signature **Groww Green (#00D09C)** is used exclusively for primary actions, success states, and positive market trends, acting as a beacon of growth against the neutral backdrop.

Neutral grays are used sparingly to define hierarchy:
- **Surface Subtle (#F9FAFB)** is used for large background sections or container fills to separate content without adding visual weight.
- **Text Primary (#121212)** provides high-contrast legibility for headlines.
- **Text Secondary (#44475B)** is used for body copy and supporting metadata.
- **Borders (#EDF2F7)** are kept extremely light to maintain a borderless, airy feel.

## Typography

This design system utilizes **Inter** across all levels to maintain a systematic, utilitarian aesthetic. The typography relies on weight and spacing rather than size shifts to convey importance.

- **Headlines:** Use Semi-Bold (600) weights with slight negative letter-spacing for a modern, compact appearance in headers.
- **Body:** Standardized at 16px for readability, using Regular (400) weight. 
- **Data Points:** For financial figures, use Medium (500) weights to ensure numbers are easily scannable.
- **Labels:** Small caps are avoided; instead, use sentence case with Medium weights to maintain the approachable, friendly tone.

## Layout & Spacing

The layout philosophy follows a **Fluid Grid** model with high-volume whitespace. A 12-column grid is used for desktop, but the layout "breathes" through large margins (40px+) to prevent the interface from feeling cramped.

**Rhythm:**
- Use an **8px base unit** for all spacing increments.
- Internal card padding is consistently **24px (lg)** to ensure data visualizations have enough room to be interpreted.
- **Smart Suggestions** and horizontal chip lists use **12px (sm)** spacing between elements to create tight, clickable groupings.

**Breakpoints:**
- **Mobile (< 600px):** Single column, 16px side margins.
- **Tablet (600px - 1024px):** 8-column grid, fluid margins.
- **Desktop (> 1024px):** 12-column grid, fixed max-width of 1440px for content.

## Elevation & Depth

This design system avoids heavy shadows, instead using **Tonal Layering** and **Low-Contrast Outlines** to define depth.

- **Level 0 (Background):** Pure #FFFFFF.
- **Level 1 (Cards/Sections):** A 1px border of #EDF2F7 or a subtle #F9FAFB fill. 
- **Interactive Elevation:** Only when an element is hovered or active, apply a very soft, diffused shadow: `0px 4px 12px rgba(0, 0, 0, 0.05)`. This creates a "lift" effect without appearing heavy.
- **Separators:** Use thin 1px lines in #EDF2F7 for list items. Avoid dividers where whitespace can naturally create the separation.

## Shapes

The shape language is "Soft and Friendly." Rounded corners are used to reduce the perceived complexity of fintech data.

- **Cards & Containers:** Use a 16px (rounded-xl equivalent) radius to create a soft, modern frame for content.
- **Buttons & Chips:** Use a **Pill-shaped (100px)** radius. This is a core differentiator for the "Smart Suggestion" aesthetic, making them look like inviting, touch-friendly bubbles.
- **Inputs:** A slightly tighter 8px (rounded-md) radius is used for text fields to maintain a sense of structural integrity.

## Components

### Buttons
Primary buttons use a full Groww Green (#00D09C) fill with white text. They should always have a pill-shaped radius. Secondary buttons should be ghost-style with a green border and green text, or a light gray fill (#F1F3F6) with dark text.

### Smart Suggestion Chips
Chips are a primary navigation and filter pattern. They should feature:
- A light background fill (#F1F3F6).
- A pill-shaped radius.
- No border in their default state.
- On selection, the background flips to #00D09C with white text.

### Input Fields
Inputs should be minimalist. Use a #F9FAFB background with a subtle 1px border. On focus, the border transitions to Groww Green. Do not use floating labels; use clear, persistent labels in `label-md` typography.

### Data Cards
Cards are the primary container for intelligence. They must have a 16px corner radius and a 1px #EDF2F7 border. Avoid background fills for cards; keep them white to blend with the global background, using the border as the sole container definition.

### Checkboxes & Radios
These should use Groww Green for the active state. The roundedness of the checkbox should be 4px to match the overall soft theme of the design system.