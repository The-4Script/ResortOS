---
name: Resort Operations System
colors:
  surface: '#f8f9fb'
  surface-dim: '#d9dadc'
  surface-bright: '#f8f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#edeef0'
  surface-container-high: '#e7e8ea'
  surface-container-highest: '#e1e2e4'
  on-surface: '#191c1e'
  on-surface-variant: '#424752'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f3'
  outline: '#727783'
  outline-variant: '#c2c6d4'
  surface-tint: '#005db6'
  primary: '#005bb2'
  on-primary: '#ffffff'
  primary-container: '#2f74ce'
  on-primary-container: '#fefcff'
  inverse-primary: '#a9c7ff'
  secondary: '#595f68'
  on-secondary: '#ffffff'
  secondary-container: '#dde3ee'
  on-secondary-container: '#5f656e'
  tertiary: '#535d68'
  on-tertiary: '#ffffff'
  tertiary-container: '#6c7681'
  on-tertiary-container: '#fdfcff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#a9c7ff'
  on-primary-fixed: '#001b3d'
  on-primary-fixed-variant: '#00468c'
  secondary-fixed: '#dde3ee'
  secondary-fixed-dim: '#c1c7d2'
  on-secondary-fixed: '#161c24'
  on-secondary-fixed-variant: '#414750'
  tertiary-fixed: '#d9e3f0'
  tertiary-fixed-dim: '#bdc7d4'
  on-tertiary-fixed: '#131d25'
  on-tertiary-fixed-variant: '#3e4852'
  background: '#f8f9fb'
  on-background: '#191c1e'
  surface-variant: '#e1e2e4'
typography:
  headline-xl:
    fontFamily: inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: -0.005em
  body-md:
    fontFamily: inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
    letterSpacing: 0em
  label-md:
    fontFamily: inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: inter
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.02em
  data-lg:
    fontFamily: ibmPlexMono
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
    letterSpacing: -0.02em
  data-md:
    fontFamily: ibmPlexMono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: -0.01em
  data-sm:
    fontFamily: ibmPlexMono
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  space-2xs: 0.25rem
  space-xs: 0.5rem
  space-sm: 0.75rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
  space-2xl: 3rem
  gutter: 1rem
  sidebar-width: 15rem
  content-max-width: 88rem
---

## Brand & Style

This design system serves resort general managers, front-desk supervisors, and operations leads overseeing high-stakes hospitality logistics: guest reservations, room turns, housekeeping schedules, and on-property amenities. 

The aesthetic is tailored for sustained daily exposure without eye strain. Drawing inspiration from modern utilitarian software like Linear and Notion, the UI removes visual noise: zero artificial drop shadows, zero gradient fills, and zero decorative chrome. Visual authority is established entirely through structural grid discipline, high-grade typographic hierarchy, restrained border boundaries, and generous negative space.

Key pillars:
- **Calm & Predictable:** High-clarity layouts that de-escalate busy hospitality operational shifts.
- **Left-Aligned Structural Rigor:** Strict vertical tracking lines across headers, metrics, and data tables.
- **Sentence Case Standard:** Applied uniformly across actions, labels, table headers, and navigation to maintain an understated, conversational tone.
- **Subtle Restraint:** Structural boundaries are defined by delicate, razor-sharp outlines over pure white cards nested inside a soft off-white canvas.

## Colors

The color palette prioritizes optical softness, separation via surface contrast, and focused semantic signaling.

- **Canvas Background (`#F7F8FA`):** A soft, cool off-white that anchors the viewport without the harsh glare of raw white.
- **Surface Elevation (`#FFFFFF`):** Pure white container surfaces that rest upon the off-white canvas, framed exclusively by hairline borders.
- **Border / Divider Gray (`#E4E7EB`):** A crisp, balanced neutral gray (1px width) used for cards, table cell dividers, input frames, and horizontal separation.
- **Text Primary (`#1B2129`):** Deep slate providing high-contrast readability without the severe edge artifacts of true `#000000`.
- **Text Secondary & Meta (`#6B7580`):** Muted cool gray for column labels, contextual hints, secondary timestamps, and supporting operational metadata.
- **Brand Accent (`#3B7DD8`):** A measured, soft cobalt blue reserved strictly for interactive state indicators, primary actions, focused form borders, active table rows, and selected navigational items.
- **Functional Semantics:**
  - Success (e.g., Clean / Inspected): `#1F8A70` text on `#EEF8F5` background, with `#D1EFE7` border.
  - Warning (e.g., Delayed Checkout / Maintenance): `#D97706` text on `#FEF3C7` background, with `#FDE68A` border.
  - Urgent (e.g., Out of Order): `#DC2626` text on `#FEF2F2` background, with `#FECACA` border.

## Typography

Typography establishes an unpretentious, crisp operational hierarchy:
- **Inter** handles standard human interface elements: titles, descriptions, status notifications, button text, and navigation labels. Sentence case is mandatory across all strings (e.g., "Add room block", "Pending maintenance", "Total guest spend").
- **IBM Plex Mono** is systematically deployed for financial amounts, currency indicators, room numbers, occupancy rates, percentages, and timestamps. Its fixed tabular alignment eliminates horizontal jitter during real-time data refreshes.
- Letter spacing is subtly tightened for headlines (`-0.01em` to `-0.02em`) to deliver modern editorial density, while secondary labels retain open spacing for scanning precision.

## Layout & Spacing

The layout is built on a responsive 12-column grid balanced by an 8pt base spatial system:

- **Desktop (1280px+):** Fixed left navigation rail (240px wide) coupled with a fluid, multi-column dashboard. Workspaces use a 24px column gutter with 32px canvas margins. Card padding is fixed at 20px or 24px to provide breathable negative space.
- **Tablet (768px - 1279px):** Left navigation collapses to an icon rail (64px) or slide-over drawer; layout switches to 8 columns with 16px gutters and 24px margins. Metrics grids reflow from 4 columns to 2x2.
- **Mobile (<768px):** Single-column stacked vertical layout. Primary workspace margins compress to 16px. Table views switch to flat card lists, maintaining full numeric visibility via mono tags.
- **Structural Alignment:** Strict left alignment is enforced. Breadcrumbs, titles, tabs, card contents, and filter controls track against identical vertical grid lines.

## Elevation & Depth

This design system intentionally rejects drop shadows, blurs, and skeuomorphic gradients. Depth and separation are achieved exclusively through surface-level contrast and hairline borders:

- **Canvas Foundation:** `#F7F8FA` acts as the base ground plane.
- **Containers & Cards:** Pure `#FFFFFF` resting on the canvas, bounded by a continuous 1px solid `#E4E7EB` border.
- **Nested Compartments:** Sub-sections inside cards (e.g., table headers, metadata footers, inner metric tiles) utilize `#F7F8FA` fill with matching `#E4E7EB` separators.
- **Popovers, Dropdowns & Modals:** Floated surfaces also retain `#FFFFFF` backgrounds with 1px solid `#E4E7EB` perimeter borders. Modals dim background context with a soft, uniform backdrop (`rgba(27, 33, 41, 0.20)`).

## Shapes

The design system maintains a clean, uniform 8px (`0.5rem`) corner radius across all core surface elements:

- **Cards, Panels & Modals:** `8px` (`0.5rem`).
- **Form Inputs, Buttons & Select Triggers:** `6px` or `8px` for unified ergonomics.
- **Data Badges & Status Chips:** `4px` to `6px` to avoid hyper-rounded pill styling, preserving the structured, dashboard-first look.
- **Avatar & Icon Surfaces:** Consistent rounded square format (`6px` to `8px`), rather than full circles, sustaining the software's geometric rhythm.

## Components

### Buttons
- **Primary:** Solid `#3B7DD8` background, `#FFFFFF` text, 8px corner radius, 1px solid `#3B7DD8`. Hover: `#326EC2`. Active: `#2B5EA6`.
- **Secondary / Default:** `#FFFFFF` background, `#1B2129` text, 1px solid `#E4E7EB`, 8px corner radius. Hover: `#F7F8FA` background, `#1B2129` text.
- **Ghost:** Transparent background, `#6B7580` text. Hover: `#F7F8FA` background, `#1B2129` text.
- **Padding:** 8px 14px for default height (36px). Font: Inter 13px/18px Medium, sentence case.

### Input Fields & Selects
- **Base State:** `#FFFFFF` fill, 1px solid `#E4E7EB`, 8px corner radius, 8px 12px padding. Text: Inter 14px `#1B2129`. Placeholder: `#9AA2AB`.
- **Focus State:** 1px solid `#3B7DD8` with zero outer glow ring.
- **Labeling:** Sentence case, Inter 12px Medium, `#6B7580`, placed above input with 4px gap.

### Cards & Metrics Tiles
- **Base Style:** `#FFFFFF` surface, 1px solid `#E4E7EB`, 8px radius, 20px padding.
- **Metric Cards:** Label positioned at top in Inter 12px `#6B7580`. Main numeric value styled in IBM Plex Mono 24px Medium `#1B2129`. Optional delta badge tucked below in 12px Mono.

### Badges & Status Chips
- **Geometry:** 4px radius, 2px 8px padding, Inter 12px Medium.
- **Neutral:** `#F7F8FA` fill, `#E4E7EB` border, `#6B7580` text.
- **Occupied / Reserved (Blue):** `#EFF6FF` fill, `#DBEAFE` border, `#1E40AF` text.
- **Clean / Ready (Green):** `#EEF8F5` fill, `#D1EFE7` border, `#1F8A70` text.
- **Maintenance (Amber):** `#FEF3C7` fill, `#FDE68A` border, `#92400E` text.

### Data Tables
- **Container:** Wrapped in a 1px solid `#E4E7EB` border with 8px radius.
- **Header Row:** `#F7F8FA` background, 1px bottom border `#E4E7EB`. Text: Inter 12px Medium `#6B7580`, left-aligned, sentence case.
- **Body Rows:** `#FFFFFF` background, 1px bottom border `#E4E7EB` (omitted on last row). Hover: `#FAFBFC`. Height: 44px.
- **Cell Alignment:** Left-aligned text in Inter 13px/14px `#1B2129`; monetary figures, room numbers, and dates rendered in IBM Plex Mono.

### Checkboxes & Radio Buttons
- **Checkboxes:** 16x16px, `#FFFFFF` fill, 1px solid `#D1D5DB`, 4px radius. Checked state: `#3B7DD8` fill with sharp white check glyph.
- **Radios:** 16x16px circle, 1px solid `#D1D5DB`. Selected: 4px centered circle of `#3B7DD8`.