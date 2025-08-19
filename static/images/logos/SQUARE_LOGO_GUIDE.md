# Square Logo Processing Guide for N-Market

## Your Current Logo

- **Format**: AI-generated image
- **Dimensions**: 1,024px × 1,024px (original)
- **Current display**: 480px × 480px
- **Type**: Square logo

## Step-by-Step Logo Setup

### Step 1: Save Your Original Logo

Save your 1,024px × 1,024px logo as:

```
static/images/logos/n-market-logo-original.png
```

### Step 2: Create Different Versions

#### For Email Templates (Main Logo)

**Filename**: `n-market-logo.png`

- **Size**: 300px × 300px
- **Use**: Email headers, general web display
- **Quality**: High (PNG format)

#### For Invoice Headers (Wide Version)

**Filename**: `n-market-logo-wide.png`

- **Size**: 300px × 100px
- **Process**:
  1. Take your square logo
  2. Add transparent padding on sides, OR
  3. Create horizontal layout with logo + text

#### For High-Quality Uses

**Filename**: `n-market-logo-hd.png`

- **Size**: 512px × 512px
- **Use**: PDF invoices, print materials

#### For Small Displays

**Filename**: `n-market-logo-small.png`

- **Size**: 64px × 64px
- **Use**: FastAPI documentation, small icons

#### For Browser Favicon

**Filename**: `favicon.ico`

- **Size**: 32px × 32px
- **Format**: ICO (convert from PNG)

## Resizing Instructions

### Option 1: Using Online Tools

1. Go to https://www.iloveimg.com/resize-image
2. Upload your 1,024px × 1,024px logo
3. Resize to each required dimension
4. Download and rename appropriately

### Option 2: Using Photoshop/GIMP

1. Open your original logo
2. Image → Image Size
3. Set width/height (maintain aspect ratio)
4. Save as PNG with transparency

### Option 3: Using AI Tools

Many AI image generators can create different aspect ratios:

- Request: "Same logo design but in horizontal/wide format"
- Specify: "300px × 100px for business letterhead"

## Creating Wide Logo Version

Since your logo is square, you have options for the wide version:

### Option A: Logo + Text Layout

```
[SQUARE LOGO] N-Market
```

### Option B: Centered with Padding

```
    [SQUARE LOGO]
```

### Option C: Redesign Request

Ask your AI tool to create a horizontal version:

- "Create a wide/horizontal version of this logo"
- "Logo design suitable for business letterhead"
- "300px width × 100px height format"

## File Placement

After creating all versions, place them here:

```
static/images/logos/
├── n-market-logo.png          ← Main square (300×300)
├── n-market-logo-wide.png     ← Horizontal (300×100)
├── n-market-logo-hd.png       ← High res square (512×512)
├── n-market-logo-small.png    ← Small square (64×64)
├── favicon.ico                ← Browser icon (32×32)
└── n-market-logo-original.png ← Your original (1024×1024)
```

## Testing Your Logo

After placing files, test by visiting:

```
http://localhost:8000/static/images/logos/n-market-logo.png
http://localhost:8000/shop/branding
```

## Current Configuration

Your system is already configured to use:

- **Main logo**: Square version in emails and general display
- **Wide logo**: Horizontal version in invoices and headers
- **High-res**: PDF generation and print materials
- **Small logo**: Documentation and small displays
- **Favicon**: Browser tab icon

## Quick Start

**Minimum required**: Just save your current logo as `n-market-logo.png` (300×300 version) and the system will work. The other versions can be added later for enhanced display quality.
