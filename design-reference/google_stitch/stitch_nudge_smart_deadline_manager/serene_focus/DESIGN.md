---
name: Serene Focus
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
  on-surface-variant: '#3d4945'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f1f1f1'
  outline: '#6d7a74'
  outline-variant: '#bdc9c3'
  surface-tint: '#006b56'
  primary: '#006954'
  on-primary: '#ffffff'
  primary-container: '#00846a'
  on-primary-container: '#f5fff9'
  inverse-primary: '#70d9ba'
  secondary: '#006d41'
  on-secondary: '#ffffff'
  secondary-container: '#95f7bb'
  on-secondary-container: '#007346'
  tertiary: '#146858'
  on-tertiary: '#ffffff'
  tertiary-container: '#358170'
  on-tertiary-container: '#f4fffa'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#8cf6d6'
  primary-fixed-dim: '#70d9ba'
  on-primary-fixed: '#002018'
  on-primary-fixed-variant: '#005140'
  secondary-fixed: '#95f7bb'
  secondary-fixed-dim: '#7adaa1'
  on-secondary-fixed: '#002110'
  on-secondary-fixed-variant: '#005230'
  tertiary-fixed: '#a6f1dd'
  tertiary-fixed-dim: '#8ad5c1'
  on-tertiary-fixed: '#00201a'
  on-tertiary-fixed-variant: '#005143'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '600'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Hanken Grotesk
    fontSize: 32px
    fontWeight: '500'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  title-md:
    fontFamily: Hanken Grotesk
    fontSize: 20px
    fontWeight: '500'
    lineHeight: 28px
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
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  container-max: 1120px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  stack-sm: 12px
  stack-md: 24px
  stack-lg: 48px
---

## Brand & Style

The design system is rooted in the philosophy of "intentional productivity." It aims to reduce cognitive load by providing a calm, sanctuary-like digital environment. The target audience includes professionals and creators who value mental clarity and deep work over frantic task management.

The visual style is a blend of **Soft Minimalism** and **Modern Utility**. It prioritizes high-quality negative space and a restricted color palette to ensure that the user's content remains the sole focus. The emotional response should be one of relief and control—a departure from the cluttered, notification-heavy interfaces typical of productivity software.

## Colors

The palette is anchored in nature-inspired greens and soft neutrals to evoke a sense of growth and composure. 

- **Primary Action**: Used for the most important functional elements, such as "Create" buttons or active states.
- **Deep Teal (Text Primary)**: Replaces traditional black for text to soften the visual contrast while maintaining peak legibility.
- **Off-white Background**: Provides a low-glare canvas that makes the white surface cards appear to "float" subtly.
- **Light Green**: Reserved for progress indicators and success states, reinforcing positive reinforcement without being jarring.

## Typography

This design system utilizes a dual-font approach. **Hanken Grotesk** is used for headlines to provide a sharp, contemporary character that feels precise yet approachable. **Inter** is used for all body text and UI labels due to its exceptional legibility and systematic nature.

Hierarchy is established through weight and color rather than excessive size differences. Use `text-secondary` for body text to keep the interface feeling "light," reserving `text-primary` for headings and active interactive elements.

## Layout & Spacing

The layout philosophy follows a **Fixed Grid** model for desktop to prevent line lengths from becoming unreadable on ultra-wide monitors, while adopting a **Fluid** approach for mobile and tablet devices.

- **The 8px Rhythm**: All spacing between elements (margins, padding, gaps) must be a multiple of 8px.
- **Vertical Air**: Large "stack" spacing (48px+) should be used between major content sections to allow the design to breathe.
- **Column Logic**: Use a 12-column grid for desktop with wide 24px gutters. For task views, center the content to minimize eye travel.

## Elevation & Depth

Depth is conveyed through **Tonal Layering** and **Low-contrast Outlines** rather than heavy shadows. 

1. **Level 0 (Background)**: The `#EEEEEE` base layer.
2. **Level 1 (Surface)**: The white `#FFFFFF` cards and containers. These should use a 1px border of `#DDDDDD` instead of a shadow.
3. **Level 2 (Interaction)**: When an element is hovered or active, apply a very soft, diffused shadow: `0 4px 20px rgba(31, 111, 95, 0.08)`. This adds a subtle "lift" using the Deep Teal hue to keep the shadow feeling integrated with the palette.

## Shapes

The shape language is consistently **Rounded**. This choice softens the professional aesthetic, making the tool feel more like a supportive companion.

- **Standard Elements**: 0.5rem (8px) for buttons, input fields, and small cards.
- **Large Containers**: 1.5rem (24px) for main content areas or modal overlays.
- **Checkboxes**: Use a slightly higher roundedness (4px) than the industry standard to maintain the friendly tone.

## Components

### Buttons
- **Primary**: Solid `#2FA084` with white text. High-padding (12px 24px) to ensure a large hit-target.
- **Secondary**: Ghost style with `#1F6F5F` border and text.
- **Ghost**: No border, `#555555` text that shifts to `#1F6F5F` on hover.

### Task Markers (To-dos)
Instead of a simple tick, use a circular "ring" indicator. When completed, the ring fills with a `#6FCF97` gradient and the text undergoes a subtle strikethrough with 50% opacity.

### Navigation Tabs
Horizontal, underline-style navigation. The active state is indicated by a 3px thick `#2FA084` bar with rounded caps, positioned 8px below the label.

### Cards
White surfaces with no shadows by default. Use 24px internal padding. Title text should be `title-md` in Deep Teal.

### Inputs
Minimalist fields with only a bottom border (`#DDDDDD`) that transitions to a 2px `#2FA084` border on focus. Labels should use the `label-sm` style, positioned above the field.

### Progress Bars
Thin (4px) tracks using `#DDDDDD` with a `#6FCF97` fill. The ends should be fully rounded (pill-shaped).