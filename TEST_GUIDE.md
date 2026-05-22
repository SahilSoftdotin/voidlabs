# VOIDLABS - Automated Test Guide

## 🧪 Running Automated Tests

The project includes a comprehensive automated test suite to verify production readiness before deployment.

### Quick Start

**Windows:**
```bash
test.bat
```

**Mac/Linux:**
```bash
chmod +x test.sh
./test.sh
```

**Using npm:**
```bash
npm run test
npm run test:full    # Lint + Build + Test
```

---

## 📋 What Gets Tested

### 1. **File System Tests** ✅
- Output folder exists (`out/`)
- Required files present:
  - `out/index.html`
  - `out/404.html`
  - `.nojekyll`
  - `.github/workflows/deploy.yml`

### 2. **Build Output Tests** ✅
- HTML structure valid
- Meta tags present
- Next.js assets referenced
- Proper DOCTYPE declaration

### 3. **SEO Tests** ✅
- Meta title and description
- OpenGraph tags
- Twitter Card tags
- JSON-LD structured data
- Canonical URLs
- robots.txt configured

### 4. **Configuration Tests** ✅
- Static export enabled (`output: 'export'`)
- Base path configured (`/voidlabs`)
- Asset prefix configured
- React strict mode
- Security headers
- ESLint rules

### 5. **Deployment Tests** ✅
- GitHub Actions workflow exists
- Node.js 20 configured
- Build command present
- Pages deployment configured

### 6. **Package Tests** ✅
- Package name correct
- Version set
- Dependencies installed
- Module type (ES Module)
- License and metadata

### 7. **Production Readiness Tests** ✅
- Documentation files exist
- `.gitignore` configured
- Environment files ignored
- Security best practices

---

## 🚀 Full Test Workflow

### Option 1: Complete Testing (Recommended)

```bash
npm run test:full
```

This runs:
1. **Linting** - `npm run lint`
2. **Building** - `npm run build`
3. **Testing** - `node scripts/test.js`

### Option 2: Test Only (After Manual Build)

```bash
npm run build
npm run test
```

### Option 3: Manual Testing

```bash
# 1. Build the project
npm run build

# 2. Run tests
node scripts/test.js

# 3. View results
# Tests output pass/fail status with detailed report
```

---

## 📊 Test Output Example

```
============================================================
  📁 FILE SYSTEM TESTS
============================================================
✓ out/index.html exists
✓ out/404.html exists
✓ out/_next/static exists
✓ .nojekyll exists
✓ .github/workflows/deploy.yml exists

============================================================
  🏗️  BUILD OUTPUT TESTS
============================================================
✓ HTML doctype declared
✓ HTML tag exists
✓ Meta charset found
✓ Viewport meta tag found
✓ Page title found
✓ Meta description found
✓ Next.js assets referenced

[... more tests ...]

============================================================
  📊 TEST REPORT
============================================================
Total Tests: 45
Passed: 45
Failed: 0
Success Rate: 100.0%

🎉 ALL TESTS PASSED! Production ready.
```

---

## ⚠️ Handling Test Failures

### Common Failures & Solutions

#### ❌ "Build output folder missing"
```bash
# Rebuild the project
npm run build
npm run test
```

#### ❌ "Configuration not found"
```bash
# Verify next.config.js has correct settings
cat next.config.js

# Should contain:
# - output: 'export'
# - basePath: '/voidlabs'
# - assetPrefix: '/voidlabs'
```

#### ❌ "SEO metadata missing"
```bash
# Check layout.tsx for metadata
cat src/app/layout.tsx

# Should export:
# - metadata object
# - viewport object
# - JSON-LD schema
```

#### ❌ "GitHub Actions workflow missing"
```bash
# Verify workflow file exists
ls .github/workflows/deploy.yml

# Should be present and valid YAML
```

---

## 🔄 Pre-Deployment Checklist

Before pushing to GitHub:

```bash
# 1. Run full test suite
npm run test:full

# 2. Verify all tests pass
# (Should see "🎉 ALL TESTS PASSED!")

# 3. Check git status
git status

# 4. Review changes
git diff

# 5. Commit
git add .
git commit -m "feat: Complete production-ready setup"

# 6. Push
git push origin main

# 7. Monitor GitHub Actions
# Go to repo → Actions → Watch deployment
```

---

## 📈 Test Coverage

| Category | Tests | Status |
|----------|-------|--------|
| File System | 5 | ✅ |
| Build Output | 7 | ✅ |
| SEO | 7 | ✅ |
| Configuration | 5 | ✅ |
| Deployment | 6 | ✅ |
| Package | 6 | ✅ |
| Production Readiness | 5 | ✅ |
| **TOTAL** | **41** | ✅ |

---

## 🛠️ Customizing Tests

To add custom tests, edit `scripts/test.js`:

```javascript
// Add a new test function
function testCustomFeature() {
  section('🎨 CUSTOM FEATURE TESTS');

  if (/* your condition */) {
    success('Feature works correctly');
  } else {
    fail('Feature not working');
  }
}

// Call it in runAllTests()
function runAllTests() {
  // ... existing tests ...
  testCustomFeature();
  generateReport();
}
```

---

## 🔍 Debugging Failed Tests

### Enable Verbose Output

Edit `scripts/test.js` and add console.log statements:

```javascript
function testBuildOutput() {
  section('🏗️  BUILD OUTPUT TESTS');
  
  const indexPath = path.join(ROOT_DIR, 'out/index.html');
  console.log(`Looking for: ${indexPath}`); // Debug line
  
  // ... rest of test
}
```

### Manual File Inspection

```bash
# Check if index.html exists
ls -la out/index.html

# View index.html content
cat out/index.html | head -50

# Count lines in output file
wc -l out/index.html

# Search for specific content
grep "VOIDLABS" out/index.html
```

---

## 📚 Test Scripts Reference

### npm Commands

```bash
npm run test              # Run test suite only
npm run test:full         # Lint + Build + Test
npm run build             # Build without testing
npm run lint              # Lint code
npm run dev               # Start dev server
```

### Direct Node Execution

```bash
node scripts/test.js      # Run test script directly
```

### Batch/Shell Scripts

```bash
# Windows
test.bat

# Mac/Linux
./test.sh
```

---

## 🎯 Success Criteria

Your project is production-ready when:

- ✅ `npm run test:full` completes successfully
- ✅ All 41+ tests pass
- ✅ Build output exists in `out/` folder
- ✅ No console errors
- ✅ All files validated

---

## 📞 Troubleshooting

### "Node.js not found" error
```bash
# Check Node.js installation
node --version

# Should output something like: v20.11.0
# If not installed, download from: https://nodejs.org/
```

### Permission denied (Mac/Linux)
```bash
# Make script executable
chmod +x test.sh
chmod +x scripts/test.js

# Then run
./test.sh
```

### Test hangs or takes too long
```bash
# Cancel and check file sizes
Ctrl+C

# If out/ folder is huge, rebuild
rm -rf out .next
npm run build
```

---

## ✨ After Tests Pass

Once all tests pass:

1. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: Add automated test suite"
   git push origin main
   ```

2. **Monitor deployment:**
   - GitHub Actions runs automatically
   - Check repo → Actions tab
   - Wait 2-3 minutes for deployment

3. **Visit live site:**
   - https://sahilsoftdotin.github.io/voidlabs/
   - Test all functionality

4. **Next steps:**
   - Monitor site performance
   - Add analytics if needed
   - Set up error tracking

---

**Happy testing! 🚀**
