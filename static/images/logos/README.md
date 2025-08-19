# Logo Implementation Guide for N-Market

## Your Logo Specifications

- **Original**: 1,024px × 1,024px (square, AI-generated)
- **Current scaling**: 480px × 480px
- **Format**: Likely PNG with good quality

## Recommended Logo Versions

Create these versions from your 1,024px × 1,024px original:

```
static/images/logos/
├── n-market-logo.png          # Main logo (300px × 300px square)
├── n-market-logo-wide.png     # Horizontal version (300px × 100px)
├── n-market-logo-hd.png       # High res square (512px × 512px)
├── n-market-logo-small.png    # Small square (64px × 64px)
├── favicon.ico                # Browser icon (32px × 32px)
└── n-market-logo-original.png # Your original (1,024px × 1,024px)
```

## Optimal Sizes for Different Uses

### 1. Email Headers (300px × 300px)

- **File**: `n-market-logo.png`
- **Use**: Email templates, general web display
- **Resize**: Scale down from 1,024px to 300px

### 2. Invoice Headers (300px × 100px horizontal)

- **File**: `n-market-logo-wide.png`
- **Use**: PDF invoices, letterheads
- **Create**: Crop or add padding to make rectangular

### 3. High Resolution (512px × 512px)

- **File**: `n-market-logo-hd.png`
- **Use**: PDF generation, print materials
- **Resize**: Scale down from 1,024px to 512px

### 4. API Documentation (64px × 64px)

- **File**: `n-market-logo-small.png`
- **Use**: FastAPI docs, small displays
- **Resize**: Scale down from 1,024px to 64px

### 5. Favicon (32px × 32px)

- **File**: `favicon.ico`
- **Use**: Browser tab icon
- **Convert**: PNG to ICO format

## Implementation Steps

1. **Add your logo files** to this directory
2. **Update .env file** if needed (already configured)
3. **Test the implementation** by accessing:
   - http://localhost:8000/static/images/logos/n-market-logo.png
   - http://localhost:8000/shop/info (API endpoint with logo URL)

## Current Configuration

Your logo is already configured in the system:

- Path: `/static/images/logos/n-market-logo.png`
- Used in: Invoices, Emails, API documentation
- Accessible via: Shop info API endpoint
