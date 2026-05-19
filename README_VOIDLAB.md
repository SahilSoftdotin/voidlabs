# VOIDLAB — Creative Studio Website

A high-performance, pixel-perfect creative studio portfolio website with custom animations, interactive elements, and modern design practices.

## 🎯 Features

✨ **Modern Design**
- Futuristic aesthetic with cyan/violet color scheme
- Smooth animations and transitions
- Custom cursor and interactive elements
- Responsive grid layout for projects

⚡ **Performance Optimized**
- Minimal dependencies
- Inline CSS for instant rendering
- Optimized Canvas particle system
- Efficient scroll reveal animations
- Lazy load support ready

🎨 **Interactive Components**
- Animated hero section with particle canvas
- Smooth scroll reveals on all sections
- Animated number counters for stats
- Custom cursor tracking
- Mobile-responsive menu
- Magnetic button effects

♿ **Accessibility**
- ARIA labels and semantic HTML
- Keyboard navigation support
- Respects prefers-reduced-motion
- Skip to main content link
- Form validation with feedback

🔍 **SEO Optimized**
- Meta tags for social sharing (OG, Twitter)
- Semantic HTML structure
- robots.txt and sitemap.xml
- Canonical URLs
- Proper heading hierarchy

## 📁 Project Structure

```
public/
├── index.html          # Main website (all-in-one)
├── manifest.json       # PWA manifest
├── robots.txt          # SEO robots file
├── sitemap.xml         # XML sitemap
└── _headers            # Security headers
```

## 🚀 Quick Start

1. **Open the website:**
   - Open `public/index.html` in a browser
   - Or serve with any static server

2. **Deploy:**
   - Deploy the `public/` folder to any static hosting
   - Works with: Netlify, Vercel, GitHub Pages, AWS S3, etc.

## 📝 Customization

### Update Contact Info
Edit in `public/index.html`:
- Email: Search for "info@voidlab" and update
- Phone: Search for "+91 90900 00876"
- Address: Update in Contact section
- Social links: Update URLs in social-links nav

### Update Company Info
- Business name: Replace "VOIDLAB" throughout
- Logo: Keep as text or replace with SVG
- Colors: Update CSS variables in `:root`
- Fonts: Edit Google Fonts link if needed

### Update Content
- Testimonials: Update names, roles, quotes
- Services: Edit service descriptions and tags
- Portfolio projects: Update project names and categories
- Stats: Update project counts and achievements

### Customize Colors
Edit CSS variables (line ~25):
```css
:root {
  --bg:          #080810;      /* Dark background */
  --cyan:        #00f0ff;      /* Primary accent */
  --violet:      #a855f7;      /* Secondary accent */
  --white:       #f0eeff;      /* Text color */
  /* ... more colors ... */
}
```

## 🔧 Server Setup

### Netlify / Vercel
1. Connect your repo
2. Set build command: (none needed)
3. Set publish directory: `public/`
4. Deploy!

### Apache (.htaccess)
Place an `.htaccess` file in `public/`:
```apache
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>

# Gzip compression
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css text/javascript application/javascript
</IfModule>

# Cache control
<FilesMatch "\.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$">
  Header set Cache-Control "max-age=31536000, public"
</FilesMatch>
```

### Local Development
```bash
# Python 3
python -m http.server 8000

# Node.js
npx http-server public/

# PHP
php -S localhost:8000 -t public/
```

## 🎭 Interactive Features

### Custom Cursor
- Auto-hides and shows with page
- Enlarges on hover over interactive elements
- Smooth easing applied

### Hero Particle Canvas
- 60 animated particles
- Dynamic connection lines
- Resizes with window
- Optimized with requestAnimationFrame

### Scroll Reveals
- Elements fade/slide into view
- Uses Intersection Observer
- Staggered animations with delays
- Respects prefers-reduced-motion

### Animated Counters
- Smooth number progression
- Eased animations
- Triggers when scrolled into view
- Customizable duration

### Mobile Menu
- Hamburger icon animation
- Smooth transitions
- Click links to auto-close
- Keyboard accessible

## 📱 Responsive Breakpoints

- **Desktop:** 1200px+ (full grid layouts)
- **Tablet:** 900px - 1199px (2-column grids)
- **Mobile:** 600px - 899px (1-column layouts)
- **Small Mobile:** < 600px (optimized text sizing)

## ♿ Accessibility Features

✅ **Implemented:**
- Semantic HTML5 elements
- ARIA labels and roles
- Keyboard navigation
- Focus management
- Color contrast compliance
- Alt text for decorative elements
- Skip link for keyboard users
- Motion preferences respected

## 🔐 Security Headers

The `_headers` file includes:
- `X-Frame-Options: SAMEORIGIN` - Prevent clickjacking
- `X-Content-Type-Options: nosniff` - Prevent MIME sniffing
- `X-XSS-Protection` - XSS protection
- `Referrer-Policy` - Privacy control
- `Content-Security-Policy` - Injection prevention

## 📊 Performance Metrics

**Optimized for:**
- **Lighthouse:** 90+ score
- **PageSpeed:** Mobile & Desktop friendly
- **Core Web Vitals:** Passing
- **Time to Interactive:** < 2 seconds
- **Bundle Size:** ~50KB (HTML + CSS + JS inline)

## 🚨 Form Handling

The contact form includes:
- Client-side validation
- Email regex check
- Required field validation
- Minimum message length
- Success/error states

**Note:** Form doesn't submit to backend. To enable:
1. Set up backend endpoint
2. Update form submission handler
3. Add CORS headers if needed

## 📦 Dependencies

**None!** This is a vanilla HTML/CSS/JavaScript single-file website.

Fonts are loaded from **Google Fonts CDN**:
- Syne (Display)
- Space Mono (Monospace)
- Cormorant Garamond (Serif)

## 🐛 Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 📄 License

Customize as needed for your business.

## 🤝 Support

For issues or customization help, refer to inline code comments in `public/index.html`.

---

**Made with ✦ for creative studios and visionary brands.**
