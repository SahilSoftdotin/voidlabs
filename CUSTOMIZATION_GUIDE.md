# VOIDLAB - Quick Customization Guide

## 📝 Essential Changes

### 1. Contact Information
**In `public/index.html`, find and update:**

**Email** (around line 1550):
```html
<!-- OLD: -->
<a href="javascript:window.location.href='mailto:'+atob('aW5mb0B2b2lkbGFicy5jb20=');">

<!-- NEW: Update encoded email -->
<!-- First, encode your email with base64:
     Use: https://www.base64encode.org/
     Then replace the encoded string -->
```

**Phone** (around line 1555):
```html
<a href="tel:+919090000876">+91 90900 00876</a>
```

**Address** (around line 1560):
```html
<span>3153 Mulberry Ter, Apt 251<br>Taylorsville, CA 95983<br>United States</span>
```

### 2. Social Media Links
**Update these URLs** (around line 1566):
```html
<a href="https://twitter.com/yourhandle">TW</a>
<a href="https://instagram.com/yourhandle">IG</a>
<a href="https://dribbble.com/yourhandle">DR</a>
<a href="https://linkedin.com/company/yourname">LI</a>
<a href="https://behance.net/yourhandle">BE</a>
```

### 3. Brand Colors
**Update CSS variables** (around line 23):
```css
:root {
  --bg:          #080810;      /* Dark background */
  --bg-2:        #0d0d1a;
  --bg-card:     #0f0f1e;
  --cyan:        #00f0ff;      /* Primary accent - CHANGE THIS */
  --violet:      #a855f7;      /* Secondary accent - CHANGE THIS */
  --white:       #f0eeff;      /* Text color */
  --muted:       #4a4a6a;      /* Muted text */
}
```

### 4. Company Name
**Global find & replace:**
- Find: `VOIDLAB`
- Replace: `Your Company Name`
- Check these places:
  - Logo (`<a href="#hero" class="nav-logo">`)
  - Footer (`<span class="footer-logo">`)
  - Manifest (`public/manifest.json`)

### 5. Hero Headline
**Update** (around line 1200):
```html
<span class="hero-title-line">We craft</span>
<span class="hero-title-line"><em class="italic">futures</em></span>
<span class="hero-title-line">worth <span class="accent">seeing.</span></span>
```

### 6. Hero Description
**Update** (around line 1220):
```html
<p class="hero-sub">
  VOIDLAB is a forward-thinking creative studio operating at the intersection of design, technology, and storytelling. We build brands that leave a mark.
</p>
```

---

## 🎨 Customization Examples

### Change Primary Color
**Before:**
```css
--cyan: #00f0ff;
```

**After (Teal):**
```css
--cyan: #14B8A6;
```

### Add Your Logo
**Replace text logo:**
```html
<!-- BEFORE: -->
<a href="#hero" class="nav-logo">VOIDLABS</a>

<!-- AFTER: -->
<a href="#hero" class="nav-logo">
  <img src="/logo.svg" alt="Company Logo" style="height: 24px; width: auto;">
</a>
```

### Update Service Cards
**Find service cards** (around line 1325):
```html
<!-- Service 1 -->
<article class="service-card reveal" role="listitem">
  <span class="service-number">01 /</span>
  <div class="service-icon" aria-hidden="true">◈</div>
  <h3 class="service-name">Brand Identity</h3>
  <p class="service-desc">Complete visual systems...</p>
  <div class="service-tags">
    <span class="service-tag">Logo Design</span>
    <!-- Add your tags -->
  </div>
</article>
```

### Update Project Portfolio
**Find project tiles** (around line 1410):
```html
<!-- Project 1 - Large -->
<article class="project-tile reveal" role="listitem">
  <div class="project-placeholder project-bg-1">IMAGE</div>
  <div class="project-overlay">
    <span class="project-cat">Brand Identity</span>
    <h3 class="project-title">NEXUS — Financial Platform</h3>
  </div>
</article>
```

### Add Real Images to Projects
**Replace placeholders with images:**
```html
<!-- Replace: -->
<div class="project-placeholder project-bg-1">IMAGE</div>

<!-- With: -->
<img src="/projects/project1.jpg" alt="NEXUS Project" class="project-img" loading="lazy">
```

### Update Testimonials
**Find testimonials** (around line 1505):
```html
<blockquote class="testimonial-card reveal">
  <p class="testimonial-text">
    "Great quote from real client..."
  </p>
  <footer class="testimonial-author">
    <div class="author-avatar">MC</div>
    <div>
      <cite class="author-name">Client Name</cite>
      <p class="author-role">Title, Company</p>
    </div>
  </footer>
</blockquote>
```

### Update Stats
**Find statistics** (around line 1485):
```html
<div class="stat-big" data-count="127">000</div>
<span class="stat-big-label">Projects Completed</span>
```

---

## 🔧 Advanced Customization

### Add Google Analytics
**Add after opening `<head>` tag:**
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_ID');
</script>
```

### Setup Netlify Forms
**In form tag:**
```html
<form id="contact-form" name="contact-form" netlify novalidate>
  <!-- form fields -->
</form>
```

### Add Favicon
1. Create 32x32 PNG icon
2. Save as `public/favicon.ico`
3. Already linked in HTML!

### Change Fonts
**Update Google Fonts link** (around line 11):
```html
<!-- Old: -->
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Space+Mono..." rel="stylesheet" />

<!-- New: Find fonts on https://fonts.google.com -->
<!-- Copy the link and paste here -->
```

Then update CSS variables:
```css
--font-display: 'Your Font', sans-serif;
--font-mono: 'Your Mono', monospace;
--font-serif: 'Your Serif', serif;
```

---

## 📱 Mobile Customization

### Adjust Mobile Menu
**Around line 1400:**
```css
.mobile-menu a {
  font-size: 2rem;  /* Change this */
}
```

### Adjust Breakpoints
**Find media queries** (around line 1100):
```css
@media (max-width: 900px) {
  /* Tablet and below */
}

@media (max-width: 600px) {
  /* Mobile only */
}
```

---

## 🚀 Performance Tweaks

### Lazy Load Images
```html
<img src="image.jpg" loading="lazy" alt="Description">
```

### Optimize Canvas Particle Count
**Line ~1750, change COUNT:**
```javascript
const COUNT = 60;  /* Change to 40 for better performance on mobile */
```

### Reduce Animation Duration
**Find animation durations:**
```css
animation: scroll-pulse 1.8s ease-in-out infinite;
/* Change 1.8s to 1.2s for faster animations */
```

---

## ✅ Testing Checklist

After customization:
- [ ] All links work
- [ ] Email obfuscation still works
- [ ] Form validates properly
- [ ] Mobile menu opens/closes
- [ ] Animations smooth
- [ ] Images load correctly
- [ ] Colors look good
- [ ] Text is readable
- [ ] No console errors
- [ ] Lighthouse score 90+

---

## 📞 Common Questions

**Q: How to add more projects?**
A: Copy a project tile block and paste it in the work grid.

**Q: How to change animation speed?**
A: Find `duration` or `transition` values in CSS, adjust timing.

**Q: How to disable animations?**
A: In CSS, change `transition-duration: 0.01ms` or animation: none;

**Q: How to add more services?**
A: Copy a service-card block and update content.

**Q: How to change form fields?**
A: Add/remove form-group divs with input/textarea elements.

