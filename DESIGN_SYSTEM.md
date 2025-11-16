# متجر رياض الإلكتروني - Design System

## Overview
This document outlines the comprehensive design system for متجر رياض الإلكتروني, a luxury e-commerce platform. The system ensures consistency, usability, and a premium user experience across all touchpoints.

## Design Principles

### 1. Luxury Aesthetic
- Premium dark theme with gold accents
- Sophisticated typography and spacing
- High-quality imagery and visual elements
- Subtle animations and transitions

### 2. User-Centered Design
- Intuitive navigation and information architecture
- Clear visual hierarchy and readability
- Accessible design for all users
- Responsive across all device sizes

### 3. Performance Focus
- Optimized loading times
- Efficient interactions
- Minimal cognitive load
- Progressive enhancement

## Color Palette

### Primary Colors
- **Primary**: `#0a192f` (Deep Navy) - Main background and structural elements
- **Secondary**: `#64ffda` (Aqua) - Accents, links, and interactive elements
- **Accent**: `#ccd6f6` (Light Blue) - Secondary text and highlights

### Surface Colors
- **Surface**: `#112240` (Dark Blue Gray) - Card backgrounds and containers
- **Surface Light**: `#233554` (Medium Blue Gray) - Form inputs and subtle backgrounds

### Text Colors
- **Text Primary**: `#ccd6f6` (Light Blue) - Main text content
- **Text Secondary**: `#8892b0` (Muted Blue) - Supporting text and descriptions
- **Text Tertiary**: `#64748b` (Gray Blue) - Placeholder text and disabled states

### Status Colors
- **Success**: `#10b981` (Emerald) - Positive actions and success states
- **Warning**: `#f59e0b` (Amber) - Cautionary information and warnings
- **Error**: `#ef4444` (Red) - Errors and destructive actions
- **Info**: `#3b82f6` (Blue) - Informational content and neutral actions

### Gradient Accents
- **Gold Gradient**: `linear-gradient(135deg, #ffd700, #ffed4e)` - Premium elements and CTAs
- **Premium Gradient**: `linear-gradient(135deg, #9d00ff, #5a00ff)` - Special offers and highlights

## Typography

### Font Family
- **Primary**: Inter (Modern sans-serif) - All text content

### Font Scale
- **Heading 1**: 3rem (48px) - Page titles
- **Heading 2**: 2.25rem (36px) - Section headers
- **Heading 3**: 1.875rem (30px) - Card titles
- **Heading 4**: 1.5rem (24px) - Subsection headers
- **Heading 5**: 1.25rem (20px) - Card subtitles
- **Heading 6**: 1.125rem (18px) - Labels and small headers
- **Body**: 1rem (16px) - Paragraph text
- **Small**: 0.875rem (14px) - Supporting text
- **Extra Small**: 0.75rem (12px) - Captions and meta information

### Font Weights
- **Light**: 300 - Minimal emphasis
- **Regular**: 400 - Body text
- **Medium**: 500 - Labels and form elements
- **Semibold**: 600 - Subheaders and navigation
- **Bold**: 700 - Headers and important text
- **Extrabold**: 800 - Page titles and hero text

## Spacing System

### Base Unit
- **Base**: 1rem (16px) - Foundational spacing unit

### Scale
- **XXS**: 0.25rem (4px) - Minimal spacing
- **XS**: 0.5rem (8px) - Tiny elements
- **SM**: 0.75rem (12px) - Small components
- **MD**: 1rem (16px) - Default spacing
- **LG**: 1.5rem (24px) - Section spacing
- **XL**: 2rem (32px) - Major sections
- **2XL**: 3rem (48px) - Page sections
- **3XL**: 4rem (64px) - Major page divisions
- **4XL**: 6rem (96px) - Hero sections

## Border Radius

### Scale
- **XS**: 0.125rem (2px) - Sharp corners
- **SM**: 0.25rem (4px) - Slight rounding
- **MD**: 0.5rem (8px) - Standard rounding
- **LG**: 0.75rem (12px) - Soft corners
- **XL**: 1rem (16px) - Pill shapes
- **2XL**: 1.5rem (24px) - Large curves
- **3XL**: 2rem (32px) - Extra large curves
- **Full**: 9999px - Circular elements

## Shadows

### Elevation
- **SM**: 0 1px 2px 0 rgba(0, 0, 0, 0.05) - Subtle depth
- **Default**: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1) - Standard elevation
- **MD**: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1) - Medium elevation
- **LG**: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1) - High elevation
- **XL**: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1) - Prominent elevation
- **2XL**: 0 25px 50px -12px rgba(0, 0, 0, 0.25) - Maximum elevation
- **Inner**: inset 0 2px 4px 0 rgba(0, 0, 0, 0.05) - Inset shadows
- **Premium**: 0 0 30px rgba(100, 255, 218, 0.2) - Luxury glow effect

## Components

### Buttons

#### Variants
1. **Primary**: Gold gradient background, dark text, used for main actions
2. **Secondary**: Surface light background, primary text, used for secondary actions
3. **Premium**: Purple gradient background, white text, used for special offers
4. **Success**: Green background, white text, used for positive actions
5. **Danger**: Red background, white text, used for destructive actions
6. **Outline**: Transparent background, secondary border, used for tertiary actions

#### Sizes
1. **Small**: Padding 0.5rem 1rem, Font size 0.875rem
2. **Medium**: Padding 0.75rem 1.5rem, Font size 1rem
3. **Large**: Padding 1rem 2rem, Font size 1.125rem
4. **Extra Large**: Padding 1.25rem 2.5rem, Font size 1.25rem

#### States
- **Default**: Base styling
- **Hover**: Elevation increase, subtle animation
- **Active**: Pressed state with reduced elevation
- **Focus**: Visible focus ring for accessibility
- **Disabled**: Reduced opacity and no interaction

### Cards

#### Structure
- **Container**: Surface background with border radius and shadow
- **Header**: Optional header section with border
- **Body**: Main content area with padding
- **Footer**: Optional footer section with border

#### Variants
1. **Standard**: Basic card with standard padding
2. **Luxury**: Premium card with gold accent on hover
3. **Interactive**: Elevated on hover with cursor change

### Forms

#### Input Fields
- **Text Inputs**: Surface light background, primary text, border styling
- **Select Dropdowns**: Custom styled selects with arrow indicators
- **Text Areas**: Multi-line inputs with resize control
- **Checkboxes**: Custom styled with clear checked states
- **Radio Buttons**: Custom styled with clear selected states

#### Labels
- **Position**: Above input fields
- **Style**: Semibold weight, secondary text color
- **Required**: Asterisk indicator for mandatory fields

#### Validation
- **Success**: Green border with checkmark icon
- **Error**: Red border with error message
- **Warning**: Amber border with warning icon

### Navigation

#### Header Navigation
- **Logo**: Left-aligned with brand identity
- **Menu Items**: Center-aligned with hover effects
- **User Actions**: Right-aligned with cart indicator

#### Breadcrumb
- **Path**: Clear navigation trail with separators
- **Current**: Bold styling for active page
- **Links**: Standard link styling for previous pages

#### Pagination
- **Numbers**: Clear page indicators
- **Arrows**: Previous/next navigation
- **Active**: Highlighted current page

### Product Display

#### Product Cards
- **Image**: Consistent aspect ratio with object fit
- **Title**: Truncated with hover expansion
- **Rating**: Star display with numerical value
- **Price**: Prominent with currency indication
- **Badges**: Visual indicators for special status

#### Product Listings
- **Grid Layout**: Responsive grid with consistent spacing
- **Filters**: Collapsible filter panel on desktop
- **Sorting**: Dropdown with clear options
- **Results**: Count and pagination controls

### Data Display

#### Tables
- **Headers**: Clear column identification
- **Rows**: Alternating background for readability
- **Cells**: Consistent padding and alignment
- **Actions**: Inline buttons for row operations

#### Lists
- **Ordered**: Numbered items with clear hierarchy
- **Unordered**: Bulleted items with visual consistency
- **Description**: Term/definition pairs with clear separation

## Icons

### Icon Set
- **Font Awesome**: Primary icon library for consistent styling
- **Custom Icons**: Brand-specific icons for unique elements

### Usage Guidelines
- **Size**: Consistent with text hierarchy
- **Color**: Match surrounding text or use accent colors
- **Spacing**: Adequate padding around icons
- **Accessibility**: Proper alt text and ARIA labels

## Animations & Transitions

### Micro-interactions
- **Button Hovers**: Subtle elevation and color shifts
- **Card Hovers**: Elevation increase and gold accent
- **Form Focus**: Glow effect and border color change
- **Loading States**: Smooth skeleton screens and spinners

### Page Transitions
- **Entrances**: Fade-in with slight upward movement
- **Exits**: Fade-out with slight downward movement
- **Navigation**: Smooth transitions between pages

### Performance Guidelines
- **Duration**: 150ms-500ms for most interactions
- **Easing**: Cubic-bezier for natural movement
- **Preferences**: Respect user's reduced motion settings

## Responsive Design

### Breakpoints
- **Small**: 0px - 768px (Mobile)
- **Medium**: 768px - 1024px (Tablet)
- **Large**: 1024px - 1200px (Desktop)
- **Extra Large**: 1200px+ (Large Desktop)

### Adaptations
- **Layout**: Grid to column reflow
- **Typography**: Scale adjustments for readability
- **Navigation**: Hamburger menu on small screens
- **Images**: Responsive sizing with aspect ratio preservation

## Accessibility

### Visual Standards
- **Contrast**: Minimum 4.5:1 for text elements
- **Focus States**: Clear visible indicators
- **Typography**: Scalable and readable fonts
- **Color**: No color-only indicators for information

### Navigation
- **Keyboard**: Full keyboard operability
- **Screen Readers**: Proper ARIA labels and roles
- **Skip Links**: Direct content access options
- **Landmarks**: Clear page structure identification

## Implementation Guidelines

### CSS Custom Properties
- **Tokens**: Design tokens for consistent theming
- **Variables**: Reusable values for spacing, colors, and typography
- **Themes**: Dark/light mode support through CSS variables

### Component Architecture
- **Modularity**: Reusable components with clear APIs
- **Composition**: Building complex interfaces from simple components
- **State Management**: Clear handling of interactive states

### Performance Optimization
- **Critical CSS**: Above-the-fold styling inlined
- **Lazy Loading**: Non-critical resources loaded on demand
- **Asset Optimization**: Compressed images and minified code

## Conclusion

This design system provides a comprehensive framework for creating a consistent, luxurious, and user-friendly e-commerce experience. By following these guidelines, all pages and components will maintain visual coherence while providing an exceptional shopping experience that reflects the premium nature of متجر رياض الإلكتروني.