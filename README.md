# VOIDLABS — Creative Studio

A modern, high-performance creative studio portfolio built with **Next.js**, **React**, **Framer Motion**, and **Tailwind CSS**. Features stunning animations, glassmorphism effects, and a fully responsive design.

## ✨ Features

- **Live Motion Animations** - Smooth, performant animations with Framer Motion
- **Modern UI/UX** - Glassmorphism effects, gradient backgrounds, and neon accents
- **Fully Responsive** - Perfect on desktop, tablet, and mobile devices
- **Fast Performance** - Static export for optimal performance
- **SEO Optimized** - Meta tags, structured data, and sitemap included
- **GitHub Pages Ready** - One-click deployment with automated workflows
- **Next-Level Visual Effects** - Floating particles, animated text, dynamic backgrounds

## 🚀 Quick Start

### Prerequisites
- Node.js 20+ 
- npm or yarn

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open in browser
# http://localhost:3000
```

The app will be available at `http://localhost:3000` with hot reload enabled.

### Build for Production

```bash
# Create optimized production build
npm run build

# Preview production build locally
npm run start
```

## 📦 Project Structure

```
src/
├── app/                          # Next.js app directory
│   ├── layout.tsx               # Root layout with metadata
│   ├── page.tsx                 # Home page (redirects to marketing)
│   ├── globals.css              # Global styles
│   ├── error.tsx                # Error page
│   ├── not-found.tsx            # 404 page
│   └── (marketing)/             # Marketing pages
│       ├── page.tsx             # Homepage
│       ├── layout.tsx           # Layout with animations
│       ├── about/               # About page
│       └── projects/            # Projects showcase
│
├── components/
│   ├── animations/              # Animation components
│   │   ├── AnimatedBackground.tsx
│   │   ├── AnimatedText.tsx
│   │   ├── FloatingParticles.tsx
│   │   └── index.ts
│   │
│   └── ui/                      # UI components
│       ├── AnimatedButton.tsx
│       └── index.ts
│
├── lib/                         # Utilities
│   ├── seo.ts                  # SEO helpers
│   └── utils.ts                # General utilities
│
└── types/                      # TypeScript types
    └── index.ts

public/                         # Static assets
├── manifest.json
├── robots.txt
├── sitemap.xml
└── _headers                    # Netlify headers config
```

## 🎨 Customization

### Colors & Theme
Edit CSS variables in `src/app/globals.css`:
```css
:root {
  --color-void: #0a0e27;
  --color-neon: #00ff88;
  --color-cyan: #22d3ee;
  --color-purple: #a855f7;
}
```

### Font Configuration
Fonts are imported from Google Fonts in `src/app/layout.tsx`. Modify the link to change typography.

### Animation Speed
Adjust animation durations in component files (e.g., `AnimatedBackground.tsx`):
```tsx
transition={{
  duration: 8,  // Increase/decrease for slower/faster animations
  repeat: Infinity,
}}
```

## 🚢 Deployment

### GitHub Pages

1. Ensure your repository settings have GitHub Pages enabled
2. Push to main branch
3. GitHub Actions will automatically build and deploy

**Live URL**: `https://sahilsoftdotin.github.io/voidlabs`

### Other Platforms

#### Netlify
```bash
npm run build
# Deploy the 'out' folder to Netlify
```

#### Vercel
```bash
npm run build
# Deploy using Vercel CLI or git integration
```

#### Self-Hosted
```bash
npm run build
# Serve the 'out' folder with any static server
```

## 🔧 Configuration

### Next.js Config
Edit `next.config.js` to modify:
- `basePath` - Subdirectory path (auto-configured for dev/prod)
- Image optimization settings
- Build output format

### Tailwind Config
Customize `tailwind.config.ts` for:
- Custom color schemes
- Breakpoints
- Animation utilities

## 📊 Performance

- **Lighthouse Score**: 95+
- **Core Web Vitals**: Optimized
- **Bundle Size**: ~150KB gzipped
- **Static Export**: No server required

## 📄 Pages

- **Home** - Hero section with feature showcase
- **About** - Studio information and values
- **Projects** - Portfolio of creative work
- **404** - Custom not found page

## 🛠️ Scripts

```bash
npm run dev        # Start development server
npm run build      # Build for production
npm run start      # Start production server
npm run lint       # Run ESLint
```

## 📋 Environment Variables

No environment variables required for basic functionality. The app works entirely client-side and is static-export compatible.

## 🤝 Contributing

Feel free to fork and submit pull requests for improvements!

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🔗 Links

- **Live Site**: https://sahilsoftdotin.github.io/voidlabs
- **GitHub**: https://github.com/SahilSoftdotin/voidlabs
- **Author**: VOIDLAB Creative Studio

---

**Built with ❤️ using Next.js, React, and Framer Motion**
