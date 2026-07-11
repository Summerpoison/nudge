---
name: Serene Productivity
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f4f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#3e4941'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f1f1f1'
  outline: '#6e7a70'
  outline-variant: '#becabf'
  surface-tint: '#006d41'
  primary: '#006d41'
  on-primary: '#ffffff'
  primary-container: '#6fcf97'
  on-primary-container: '#005733'
  inverse-primary: '#7adaa1'
  secondary: '#006b56'
  on-secondary: '#ffffff'
  secondary-container: '#8cf6d6'
  on-secondary-container: '#00725b'
  tertiary: '#186a5a'
  on-tertiary: '#ffffff'
  tertiary-container: '#80cab7'
  on-tertiary-container: '#005648'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#95f7bb'
  primary-fixed-dim: '#7adaa1'
  on-primary-fixed: '#002110'
  on-primary-fixed-variant: '#005230'
  secondary-fixed: '#8cf6d6'
  secondary-fixed-dim: '#70d9ba'
  on-secondary-fixed: '#002018'
  on-secondary-fixed-variant: '#005140'
  tertiary-fixed: '#a6f1dd'
  tertiary-fixed-dim: '#8ad5c1'
  on-tertiary-fixed: '#00201a'
  on-tertiary-fixed-variant: '#005143'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  display:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '600'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.5rem
  DEFAULT: 1rem
  md: 1.5rem
  lg: 2rem
  xl: 3rem
  full: 9999px
spacing:
  unit: 8px
  container-max: 1120px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  section-gap: 64px
---

## Brand & Style
The design system focuses on "Nudge," a productivity platform designed to reduce cognitive load and mitigate work-induced anxiety. The brand personality is encouraging, quiet, and spacious, acting as a digital deep breath for the user. 

The aesthetic leverages **Soft Minimalism** combined with **Organic Tactility**. By utilizing significant whitespace and a muted, nature-inspired palette, the interface avoids the frantic density of traditional project management tools. The emotional response should be one of "controlled calm"—where tasks feel achievable rather than overwhelming. High-radius corners and soft, diffused shadows are used to remove visual "sharpness" from the environment.

## Colors
The palette is rooted in a "Forest Air" theme, prioritizing low-contrast transitions to soothe the eyes.

- **Surface & Background**: `#EEEEEE` serves as the foundation, providing a soft, non-white canvas that reduces screen glare.
- **Action & Focus**: `#6FCF97` (Soft Green) is the primary interactive color, used for positive reinforcement and primary calls to action.
- **Success & Progression**: `#2FA084` (Seafoam Green) handles secondary actions and completed states, offering a clear but calm distinction from the primary action.
- **Typography & Depth**: `#1F6F5F` (Deep Forest Green) is used for all text and high-contrast borders to maintain readability without the harshness of pure black.

## Typography
The system uses **Inter** exclusively to ensure a systematic, highly legible experience. 

The typographic hierarchy is intentionally "flat"—meaning font size jumps are moderate rather than extreme. This prevents any single piece of information from feeling "shouted." 
- **Tracking**: Tighten tracking slightly on larger headlines (-0.02em) to maintain a cohesive visual unit.
- **Color Application**: Use the Deep Forest Green (`#1F6F5F`) for all headings. For secondary body text, use the same color at 70% opacity to create a soft gray-green effect.

## Layout & Spacing
The design system utilizes a **Fluid-Fixed Hybrid** model. Content is centered within a maximum container width of 1120px to prevent line lengths from becoming unreadable on wide monitors.

- **The 8px Rhythm**: All padding, margins, and gaps must be multiples of 8px.
- **Whitespace as a Feature**: Large sections should be separated by at least 64px (`section-gap`) to allow the layout to "breathe."
- **Grid**: A 12-column grid is used for desktop, collapsing to a single column for mobile. Gutters are kept wide (24px) to emphasize the airy feel.

## Elevation & Depth
In keeping with the relaxed aesthetic, this design system avoids heavy shadows. 

- **Ambient Elevation**: Depth is primarily created through subtle shifts in surface color (e.g., a white card on the `#EEEEEE` background).
- **Soft Shadows**: When elevation is required for interactivity (like a hovering task card), use a "Long-Soft" shadow: `0 10px 30px rgba(31, 111, 95, 0.08)`. This uses a tiny hint of the Deep Forest Green in the shadow to make it feel integrated with the environment rather than a "dirty" gray.
- **Layering**: Use no more than three levels of Z-index: Background (Level 0), Cards (Level 1), and Modals/Floating Actions (Level 2).

## Shapes
The shape language is defined by extreme roundedness to evoke friendliness and safety. 

- **Base Radius**: 16px (1rem) for standard components.
- **Large Radius**: 32px (2rem) for task cards and main containers (referred to as `rounded-2xl` in many frameworks).
- **Pill Shapes**: Used for buttons and status indicators to emphasize the "Nudge" brand identity—soft, rolling edges with no sharp points.

## Components

- **Task Cards**: Large, expansive white surfaces with `rounded-2xl` corners. Padding inside cards should be generous (min 24px). Headers within cards use `headline-md`.
- **Buttons**: All buttons are pill-shaped. The Primary Button uses a `#6FCF97` fill with `#1F6F5F` text. Secondary buttons are outlined with a 1.5px stroke of `#2FA084`.
- **Progress Indicators**: Instead of clinical bars, use "Organic Rings" or "Soft Blobs"—variable width strokes and rounded end-caps. Progress should feel like a growing vine rather than a loading machine.
- **Input Fields**: Soft gray-green backgrounds (`rgba(31, 111, 95, 0.05)`) with no initial border. Upon focus, a 2px stroke of the primary green appears.
- **Navigation**: A minimal sidebar with large icon-and-label pairs. Active states are indicated by a soft green "blob" background behind the icon, rather than a vertical bar.
- **Chips/Labels**: Used for task tagging. These should have a background color of 10% opacity of the category color to remain "airy" and unobtrusive.