# VOIDLABS - Production Setup Guide

This document outlines the production-ready setup for the VOIDLABS project.

## 📋 Project Overview

**VOIDLABS** is a static Next.js application deployed to GitHub Pages with comprehensive optimization and security best practices.

- **Framework:** Next.js 16 with React 19
- **Styling:** Tailwind CSS 4.3 with PostCSS
- **Deployment:** GitHub Pages (automatic via GitHub Actions)
- **Environment:** Node.js 20+

## 🚀 Deployment

### Automatic Deployment (GitHub Actions)

The project uses GitHub Actions to automatically build and deploy to GitHub Pages on every push to `main`.

**Workflow file:** `.github/workflows/deploy.yml`

**What happens automatically:**
1. ✅ Installs dependencies
2. ✅ Builds the Next.js app with static export
3. ✅ Optimizes production assets
4. ✅ Deploys to GitHub Pages

**Live URL:** https://sahilsoftdotin.github.io/voidlabs

### Manual Deployment

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Output is generated in the `out/` directory
# GitHub Actions automatically deploys this via GitHub Pages
```

## 🔒 Security Features

### Implemented Security Measures

1. **Content Security Policy (CSP)**
   - Defined in `public/_headers` (reference for future server deployments)
   - Next.js app enforces strict CSP headers

2. **Security Headers**
   - `X-Frame-Options: SAMEORIGIN` - Prevents clickjacking
   - `X-Content-Type-Options: nosniff` - Prevents MIME sniffing
   - `X-XSS-Protection` - Enables XSS protection
   - `Referrer-Policy: strict-origin-when-cross-origin`

3. **No Server-Side Secrets**
   - Static export means no sensitive data exposure
   - All secrets excluded via `.gitignore`

4. **Dependency Security**
   - Regular npm audit checks
   - Only production dependencies included in build

## ⚡ Performance Optimizations

### Configured Optimizations

```javascript
// next.config.js settings
- Image optimization (WebP, AVIF formats)
- Font optimization
- Compression enabled
- Source maps disabled in production
- Package import optimization
- Trailing slash disabled for clean URLs
```

### Best Practices Implemented

1. **Static Export**
   - Zero JavaScript bloat for static pages
   - Pre-rendered HTML for fast first paint
   - Minimal CSS bundle size with Tailwind

2. **Asset Optimization**
   - Images: WebP and AVIF support
   - Fonts: Google Fonts preconnect
   - CSS: Purged unused styles via Tailwind

3. **Caching**
   - Long-term caching via asset hashing (`_next/static/`)
   - GitHub Pages cache headers

## 📱 SEO & Meta Tags

### Implemented SEO Features

- ✅ Comprehensive meta tags (title, description, keywords)
- ✅ Open Graph tags for social sharing
- ✅ Twitter Card metadata
- ✅ Structured data (JSON-LD) for schema.org
- ✅ Canonical URLs
- ✅ Mobile viewport configuration
- ✅ robots.txt with sitemap reference
- ✅ sitemap.xml generation

### Meta Configuration

All SEO metadata is configured in `src/app/layout.tsx`:

```typescript
export const metadata: Metadata = {
  title: '...',
  description: '...',
  openGraph: { /* social media preview */ },
  twitter: { /* twitter card */ },
  // ... more metadata
}
```

## 🌐 Environment Configuration

### Environment Variables

Create `.env.local` (not committed to Git):

```bash
cp .env.example .env.local
```

**Available variables:**
- `NEXT_PUBLIC_SITE_URL` - Your site URL
- `NEXT_PUBLIC_SITE_NAME` - Site name
- `NODE_ENV` - Environment (production/development)

## 📊 Monitoring & Analytics

### Recommended Additions (Future)

```bash
# Google Analytics (if needed)
npm install next-google-analytics

# Error tracking (Sentry)
npm install @sentry/nextjs

# Performance monitoring
npm install web-vitals
```

## 🔧 Development Workflow

### Local Development

```bash
# Install dependencies
npm install

# Start dev server (http://localhost:3000)
npm run dev

# Build for production
npm run build

# Lint code
npm lint
```

### Testing Locally

```bash
# Build and test production output
npm run build
# Navigate to `out/` folder to test locally
```

## 📦 Dependencies

### Production Dependencies
- `next@^16.2.6` - React framework
- `react@^19.2.6` - UI library
- `react-dom@^19.2.6` - React DOM

### Development Dependencies
- `typescript@^6.0.3` - Type checking
- `tailwindcss@^4.3.0` - CSS framework
- `@tailwindcss/postcss@^4.3.0` - PostCSS plugin
- `eslint` - Code linting
- `postcss` - CSS processing
- `autoprefixer` - CSS vendor prefixes

## 🗂️ Project Structure

```
voidlabs/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions deployment
├── public/
│   ├── _headers                # Security headers reference
│   ├── manifest.json           # PWA manifest
│   ├── robots.txt              # SEO robots file
│   ├── sitemap.xml             # SEO sitemap
│   └── projects/               # Static project pages
├── src/
│   └── app/
│       ├── layout.tsx          # Root layout with SEO
│       ├── page.tsx            # Home page
│       └── globals.css         # Global styles
├── .env.example                # Environment variables template
├── .nojekyll                   # GitHub Pages Jekyll disable
├── next.config.js              # Next.js configuration
├── tailwind.config.ts          # Tailwind CSS config
├── tsconfig.json               # TypeScript config
└── package.json                # Dependencies
```

## 🚢 Deployment Checklist

Before deploying major updates:

- [ ] Run `npm run build` locally to verify build succeeds
- [ ] Test in `out/` directory locally
- [ ] Check all metadata and SEO tags are correct
- [ ] Run `npm lint` for code quality
- [ ] Verify all links work (especially with `/voidlabs` basePath)
- [ ] Commit and push to `main` branch
- [ ] Verify GitHub Actions workflow completes successfully
- [ ] Test live site at https://sahilsoftdotin.github.io/voidlabs

## 🔐 GitHub Pages Settings

Required GitHub repository settings:

1. Go to **Settings** → **Pages**
2. **Source:** `GitHub Actions`
3. **Branch:** `main` (automatic)
4. **Directory:** `/` (automatic)

## 📝 Important Notes

### GitHub Pages Specifics

- Site is served from `/voidlabs/` subdirectory
- All assets use `basePath: '/voidlabs'` prefix
- Static export is required (no server-side rendering)
- `_nojekyll` file prevents Jekyll processing

### Performance Tips

- Images should be optimized before upload
- Use WebP format for better compression
- Lazy load images when possible
- Minimize custom fonts (already using Google Fonts)

### Security Reminders

- ❌ Never commit `.env.local` files
- ❌ Never hardcode API keys or secrets
- ✅ Always use environment variables for sensitive data
- ✅ Keep dependencies updated: `npm audit fix`

## 🆘 Troubleshooting

### Site Not Showing

1. Check GitHub Actions workflow for errors
2. Verify GitHub Pages source is set to "GitHub Actions"
3. Clear browser cache and hard refresh
4. Check that `basePath` is correctly set to `/voidlabs`

### Build Fails

1. Ensure Node.js version is 20+
2. Run `npm install` to update dependencies
3. Check for TypeScript errors: `npx tsc --noEmit`
4. Clear `.next` folder: `rm -rf .next out`

### Links Don't Work

1. Verify all links include `/voidlabs/` prefix
2. Use relative paths or ensure basePath is applied
3. Check console for 404 errors

## 📚 Additional Resources

- [Next.js Static Export](https://nextjs.org/docs/app/building-your-application/deploying/static-exports)
- [GitHub Pages with GitHub Actions](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#deploying-with-a-build-tool)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Next.js Configuration](https://nextjs.org/docs/app/api-reference/next-config-js)

---

**Last Updated:** May 20, 2026
**Status:** ✅ Production Ready
