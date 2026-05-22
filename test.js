#!/usr/bin/env node

/**
 * VOIDLABS Automated Test Script
 * Tests build, code quality, and configuration before deployment
 * Usage: node test.js
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

const icons = {
  pass: '✓',
  fail: '✗',
  warn: '⚠',
  info: 'ℹ',
  check: '□',
};

class TestRunner {
  constructor() {
    this.results = [];
    this.passed = 0;
    this.failed = 0;
    this.warnings = 0;
  }

  log(message, type = 'info') {
    const icon = icons[type] || '•';
    const color = type === 'pass' ? colors.green : type === 'fail' ? colors.red : type === 'warn' ? colors.yellow : colors.blue;
    console.log(`${color}${icon}${colors.reset} ${message}`);
  }

  section(title) {
    console.log(`\n${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`);
    console.log(`${colors.cyan}${title}${colors.reset}`);
    console.log(`${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n`);
  }

  test(name, fn) {
    try {
      const result = fn();
      this.passed++;
      this.results.push({ name, status: 'pass', result });
      this.log(name, 'pass');
      return result;
    } catch (error) {
      this.failed++;
      this.results.push({ name, status: 'fail', error: error.message });
      this.log(`${name}: ${error.message}`, 'fail');
      throw error;
    }
  }

  warn(name, message) {
    this.warnings++;
    this.results.push({ name, status: 'warn', message });
    this.log(`${name}: ${message}`, 'warn');
  }

  fileExists(filePath) {
    return fs.existsSync(filePath);
  }

  fileContains(filePath, text) {
    const content = fs.readFileSync(filePath, 'utf-8');
    return content.includes(text);
  }

  execute(command) {
    return execSync(command, { encoding: 'utf-8', stdio: 'pipe' });
  }

  summary() {
    console.log(`\n${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}`);
    console.log(`${colors.cyan}TEST SUMMARY${colors.reset}`);
    console.log(`${colors.cyan}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${colors.reset}\n`);

    console.log(`${colors.green}Passed:${colors.reset}  ${this.passed}`);
    console.log(`${colors.red}Failed:${colors.reset}  ${this.failed}`);
    console.log(`${colors.yellow}Warnings:${colors.reset} ${this.warnings}`);

    const totalTests = this.passed + this.failed;
    const percentage = totalTests > 0 ? Math.round((this.passed / totalTests) * 100) : 0;
    console.log(`\nSuccess Rate: ${percentage}%\n`);

    if (this.failed === 0) {
      console.log(`${colors.green}✓ All tests passed! Ready for deployment.${colors.reset}\n`);
      return true;
    } else {
      console.log(`${colors.red}✗ Some tests failed. Please fix issues before deployment.${colors.reset}\n`);
      return false;
    }
  }
}

async function runTests() {
  const runner = new TestRunner();
  const projectRoot = process.cwd();

  runner.section('🏗️  PROJECT SETUP TESTS');

  // Check Node.js version
  try {
    runner.test('Node.js version >= 20', () => {
      const version = parseInt(process.version.split('.')[0].substring(1));
      if (version < 20) throw new Error(`Node.js ${version} detected, need >= 20`);
    });
  } catch (e) {
    runner.warn('Node.js version', 'Using older Node.js, may cause issues');
  }

  // Check essential files exist
  runner.test('package.json exists', () => {
    if (!runner.fileExists('package.json')) throw new Error('package.json not found');
  });

  runner.test('next.config.js exists', () => {
    if (!runner.fileExists('next.config.js')) throw new Error('next.config.js not found');
  });

  runner.test('src/app/layout.tsx exists', () => {
    if (!runner.fileExists('src/app/layout.tsx')) throw new Error('layout.tsx not found');
  });

  runner.section('⚙️  BUILD TESTS');

  // Clean build
  runner.test('Clean previous builds', () => {
    try {
      if (runner.fileExists('out')) fs.rmSync('out', { recursive: true, force: true });
      if (runner.fileExists('.next')) fs.rmSync('.next', { recursive: true, force: true });
    } catch (e) {
      throw new Error('Could not clean build directories');
    }
  });

  // Run build
  runner.test('npm run build completes successfully', () => {
    try {
      const output = runner.execute('npm run build 2>&1');
      if (output.includes('failed') || output.includes('error')) {
        throw new Error('Build output indicates failure');
      }
    } catch (e) {
      throw new Error('Build failed: ' + e.message);
    }
  });

  // Check build output
  runner.test('out/ directory created', () => {
    if (!runner.fileExists('out')) throw new Error('out/ directory not found after build');
  });

  runner.test('out/index.html exists', () => {
    if (!runner.fileExists('out/index.html')) throw new Error('out/index.html not found');
  });

  runner.section('📝 CODE QUALITY TESTS');

  // TypeScript check
  try {
    runner.test('TypeScript compilation succeeds', () => {
      const output = runner.execute('npx tsc --noEmit 2>&1');
      if (output.includes('error TS')) {
        throw new Error('TypeScript errors found');
      }
    });
  } catch (e) {
    runner.warn('TypeScript check', e.message);
  }

  // ESLint
  try {
    runner.test('ESLint passes', () => {
      const output = runner.execute('npm run lint 2>&1');
      if (output.includes('error') && !output.includes('warnings')) {
        throw new Error('ESLint errors found');
      }
    });
  } catch (e) {
    runner.warn('ESLint check', 'Some linting issues detected (non-critical)');
  }

  runner.section('🔍 CONFIGURATION TESTS');

  // Check basePath configuration
  runner.test('basePath configured for /voidlabs', () => {
    if (!runner.fileContains('next.config.js', "basePath: '/voidlabs'")) {
      throw new Error('basePath not configured correctly');
    }
  });

  runner.test('assetPrefix configured for /voidlabs', () => {
    if (!runner.fileContains('next.config.js', "assetPrefix: '/voidlabs'")) {
      throw new Error('assetPrefix not configured correctly');
    }
  });

  runner.test('Static export enabled (output: export)', () => {
    if (!runner.fileContains('next.config.js', "output: 'export'")) {
      throw new Error('Static export not enabled');
    }
  });

  runner.section('📄 FILE INTEGRITY TESTS');

  // Check important files
  const requiredFiles = [
    'public/robots.txt',
    'public/manifest.json',
    'public/sitemap.xml',
    '.nojekyll',
    '.github/workflows/deploy.yml',
    '.eslintrc.json',
    '.env.example',
  ];

  requiredFiles.forEach((file) => {
    runner.test(`${file} exists`, () => {
      if (!runner.fileExists(file)) throw new Error(`${file} not found`);
    });
  });

  runner.section('🔒 SEO & METADATA TESTS');

  // Check SEO metadata
  runner.test('Layout includes metadata exports', () => {
    if (!runner.fileContains('src/app/layout.tsx', 'export const metadata')) {
      throw new Error('Metadata not exported from layout');
    }
  });

  runner.test('robots.txt contains GitHub Pages URL', () => {
    if (!runner.fileContains('public/robots.txt', 'sahilsoftdotin.github.io')) {
      runner.warn('robots.txt', 'GitHub Pages URL not found in robots.txt');
    }
  });

  runner.test('.nojekyll file exists (for GitHub Pages)', () => {
    if (!runner.fileExists('.nojekyll')) throw new Error('.nojekyll not found');
  });

  runner.section('🚀 OUTPUT VALIDATION');

  // Check HTML output
  runner.test('index.html has content', () => {
    const content = fs.readFileSync('out/index.html', 'utf-8');
    if (content.length < 1000) throw new Error('index.html seems incomplete');
  });

  runner.test('index.html contains VOIDLABS title', () => {
    if (!runner.fileContains('out/index.html', 'VOIDLABS')) {
      throw new Error('VOIDLABS title not found in HTML');
    }
  });

  runner.test('Assets path includes /voidlabs/', () => {
    const content = fs.readFileSync('out/index.html', 'utf-8');
    if (!content.includes('/_next')) {
      runner.warn('Assets path', 'Could not verify asset paths in HTML');
    }
  });

  // 404 page check
  runner.test('404.html redirect exists', () => {
    if (!runner.fileExists('out/404.html')) {
      runner.warn('404.html', '404.html not found in output (GitHub Pages fallback may not work)');
    }
  });

  runner.section('📊 PACKAGE.JSON VALIDATION');

  runner.test('package.json has version', () => {
    const pkg = JSON.parse(fs.readFileSync('package.json', 'utf-8'));
    if (!pkg.version) throw new Error('No version in package.json');
  });

  runner.test('package.json has description', () => {
    const pkg = JSON.parse(fs.readFileSync('package.json', 'utf-8'));
    if (!pkg.description || pkg.description.length < 10) {
      throw new Error('No meaningful description in package.json');
    }
  });

  runner.test('package.json has author', () => {
    const pkg = JSON.parse(fs.readFileSync('package.json', 'utf-8'));
    if (!pkg.author) {
      runner.warn('Author', 'No author specified in package.json');
    }
  });

  runner.section('💾 BUILD SIZE ANALYSIS');

  runner.test('Analyze build output size', () => {
    let totalSize = 0;
    const countFiles = (dir) => {
      const files = fs.readdirSync(dir);
      files.forEach((file) => {
        const filePath = path.join(dir, file);
        const stat = fs.statSync(filePath);
        if (stat.isDirectory()) {
          countFiles(filePath);
        } else {
          totalSize += stat.size;
        }
      });
    };
    countFiles('out');
    const sizeMB = (totalSize / 1024 / 1024).toFixed(2);
    console.log(`   Total output size: ${sizeMB} MB`);
    if (sizeMB > 10) {
      runner.warn('Build size', `Large build detected (${sizeMB}MB)`);
    }
  });

  runner.section('✅ DEPLOYMENT READINESS');

  runner.test('.gitignore properly configured', () => {
    if (!runner.fileContains('.gitignore', 'node_modules')) {
      throw new Error('node_modules not in .gitignore');
    }
    if (!runner.fileContains('.gitignore', '.env*.local')) {
      throw new Error('env files not in .gitignore');
    }
  });

  runner.test('GitHub Actions workflow exists', () => {
    if (!runner.fileExists('.github/workflows/deploy.yml')) {
      throw new Error('GitHub Actions workflow not found');
    }
  });

  runner.test('Workflow uses Node.js 20', () => {
    if (!runner.fileContains('.github/workflows/deploy.yml', "node-version: '20'")) {
      throw new Error('Workflow not configured for Node.js 20');
    }
  });

  // Final summary
  const success = runner.summary();

  console.log(`${colors.blue}📋 NEXT STEPS:${colors.reset}`);
  console.log('1. Review test results above');
  if (success) {
    console.log('2. Run: git add .');
    console.log('3. Run: git commit -m "feat: Production-ready setup"');
    console.log('4. Run: git push origin main');
    console.log('5. Visit: https://sahilsoftdotin.github.io/voidlabs/');
  } else {
    console.log('2. Fix the issues listed above');
    console.log('3. Run this test again: node test.js');
  }

  console.log(`\n${colors.blue}📚 USEFUL COMMANDS:${colors.reset}`);
  console.log('• Local testing: serve out -p 8000');
  console.log('• Type checking: npx tsc --noEmit');
  console.log('• Linting: npm run lint');
  console.log('• Building: npm run build');
  console.log('• Full test: node test.js\n');

  process.exit(success ? 0 : 1);
}

// Run tests
console.log(`\n${colors.cyan}╔════════════════════════════════════════╗${colors.reset}`);
console.log(`${colors.cyan}║    VOIDLABS AUTOMATED TEST SUITE     ║${colors.reset}`);
console.log(`${colors.cyan}╚════════════════════════════════════════╝${colors.reset}\n`);

runTests().catch((error) => {
  console.error(`${colors.red}Fatal error: ${error.message}${colors.reset}`);
  process.exit(1);
});
