#!/usr/bin/env node

/**
 * VOIDLABS - Automated Test Suite
 * Tests build output, SEO, and production readiness
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT_DIR = path.join(__dirname, '..');

// Color codes for console output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
};

// Test results
let totalTests = 0;
let passedTests = 0;
let failedTests = 0;
const failedList = [];

/**
 * Colored console output
 */
function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function success(message) {
  log(`✓ ${message}`, 'green');
  passedTests++;
  totalTests++;
}

function fail(message) {
  log(`✗ ${message}`, 'red');
  failedTests++;
  totalTests++;
  failedList.push(message);
}

function info(message) {
  log(`ℹ ${message}`, 'blue');
}

function section(title) {
  log(`\n${'='.repeat(60)}`, 'cyan');
  log(`  ${title}`, 'cyan');
  log(`${'='.repeat(60)}`, 'cyan');
}

/**
 * File system tests
 */
function testFileSystem() {
  section('📁 FILE SYSTEM TESTS');

  const requiredFiles = [
    'out/index.html',
    'out/404.html',
    'out/_next/static',
    '.nojekyll',
    '.github/workflows/deploy.yml',
  ];

  requiredFiles.forEach(file => {
    const fullPath = path.join(ROOT_DIR, file);
    if (fs.existsSync(fullPath)) {
      success(`${file} exists`);
    } else {
      fail(`${file} missing`);
    }
  });
}

/**
 * Build output tests
 */
function testBuildOutput() {
  section('🏗️  BUILD OUTPUT TESTS');

  const indexPath = path.join(ROOT_DIR, 'out/index.html');

  try {
    const indexContent = fs.readFileSync(indexPath, 'utf8');

    // Test HTML structure
    if (indexContent.includes('<!DOCTYPE html>')) {
      success('HTML doctype declared');
    } else {
      fail('Missing HTML doctype');
    }

    if (indexContent.includes('<html')) {
      success('HTML tag exists');
    } else {
      fail('Missing HTML tag');
    }

    // Test for common meta tags
    // Note: charset is auto-injected by Next.js and may not be visible in source
    const metaTests = [
      { pattern: /viewport/, name: 'Viewport meta tag' },
      { pattern: /VOIDLABS/, name: 'Page title' },
      { pattern: /description/, name: 'Meta description' },
    ];

    metaTests.forEach(({ pattern, name }) => {
      if (pattern.test(indexContent)) {
        success(`${name} found`);
      } else {
        fail(`${name} missing`);
      }
    });

    // Test for React/Next.js
    if (indexContent.includes('_next')) {
      success('Next.js assets referenced');
    } else {
      fail('Next.js assets not found');
    }

  } catch (error) {
    fail(`Error reading index.html: ${error.message}`);
  }
}

/**
 * SEO tests
 */
function testSEO() {
  section('🔍 SEO TESTS');

  const layoutPath = path.join(ROOT_DIR, 'src/app/layout.tsx');
  const robotsPath = path.join(ROOT_DIR, 'public/robots.txt');

  try {
    const layoutContent = fs.readFileSync(layoutPath, 'utf8');

    const seoTests = [
      { pattern: /title/, name: 'Meta title' },
      { pattern: /description/, name: 'Meta description' },
      { pattern: /keywords/, name: 'Meta keywords' },
      { pattern: /openGraph|og:/, name: 'OpenGraph tags' },
      { pattern: /twitter|card/, name: 'Twitter Card tags' },
      { pattern: /"@type":|@context/, name: 'Structured data/JSON-LD' },
      { pattern: /canonical/, name: 'Canonical URL' },
    ];

    seoTests.forEach(({ pattern, name }) => {
      if (pattern.test(layoutContent)) {
        success(`${name} configured`);
      } else {
        fail(`${name} missing`);
      }
    });

  } catch (error) {
    fail(`Error testing SEO: ${error.message}`);
  }

  // Test robots.txt
  try {
    const robotsContent = fs.readFileSync(robotsPath, 'utf8');
    if (robotsContent.includes('User-agent') && robotsContent.includes('Sitemap')) {
      success('robots.txt properly configured');
    } else {
      fail('robots.txt missing required content');
    }
  } catch (error) {
    fail(`Error reading robots.txt: ${error.message}`);
  }
}

/**
 * Configuration tests
 */
function testConfiguration() {
  section('⚙️  CONFIGURATION TESTS');

  const configPath = path.join(ROOT_DIR, 'next.config.js');
  const eslintPath = path.join(ROOT_DIR, '.eslintrc.json');

  try {
    const configContent = fs.readFileSync(configPath, 'utf8');

    const configTests = [
      { pattern: /output:\s*['"]export['"]/, name: 'Static export enabled' },
      { pattern: /basePath:\s*['"]\/voidlabs['"]/, name: 'basePath configured' },
      { pattern: /assetPrefix:\s*['"]\/voidlabs['"]/, name: 'assetPrefix configured' },
      { pattern: /reactStrictMode/, name: 'React strict mode' },
      { pattern: /poweredByHeader:\s*false/, name: 'Security header removed' },
    ];

    configTests.forEach(({ pattern, name }) => {
      if (pattern.test(configContent)) {
        success(`${name}`);
      } else {
        fail(`${name} not configured`);
      }
    });

  } catch (error) {
    fail(`Error reading next.config.js: ${error.message}`);
  }

  // Test ESLint config
  try {
    const eslintContent = fs.readFileSync(eslintPath, 'utf8');
    if (eslintContent.includes('rules')) {
      success('ESLint rules configured');
    } else {
      fail('ESLint rules not configured');
    }
  } catch (error) {
    fail(`Error reading .eslintrc.json: ${error.message}`);
  }
}

/**
 * Deployment tests
 */
function testDeployment() {
  section('🚀 DEPLOYMENT TESTS');

  const workflowPath = path.join(ROOT_DIR, '.github/workflows/deploy.yml');

  try {
    const workflowContent = fs.readFileSync(workflowPath, 'utf8');

    const deployTests = [
      { pattern: /node-version.*20/, name: 'Node.js 20 configured' },
      { pattern: /ubuntu-latest|actions/, name: 'GitHub Actions workflow' },
      { pattern: /upload.*artifact|pages-artifact/, name: 'Pages artifact upload' },
      { pattern: /deploy.*pages|deploy-pages/, name: 'Pages deployment' },
      { pattern: /npm ci|npm install/, name: 'Dependency installation' },
      { pattern: /npm run build|build.*next/, name: 'Build command' },
    ];

    deployTests.forEach(({ pattern, name }) => {
      if (pattern.test(workflowContent)) {
        success(`${name}`);
      } else {
        fail(`${name} not found`);
      }
    });

  } catch (error) {
    fail(`Error reading workflow: ${error.message}`);
  }
}

/**
 * Package configuration tests
 */
function testPackageConfig() {
  section('📦 PACKAGE CONFIGURATION TESTS');

  const packagePath = path.join(ROOT_DIR, 'package.json');

  try {
    const packageContent = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

    const packageTests = [
      { field: 'name', value: 'voidlabs', name: 'Package name' },
      { field: 'version', value: '1.0.0', name: 'Version set' },
      { field: 'license', value: 'MIT', name: 'License' },
      { field: 'homepage', name: 'Homepage URL' },
      { field: 'repository', name: 'Repository info' },
      { field: 'type', value: 'module', name: 'ES Module type' },
    ];

    packageTests.forEach(({ field, value, name }) => {
      if (packageContent[field]) {
        if (value && packageContent[field] !== value) {
          fail(`${name} incorrect`);
        } else {
          success(`${name}`);
        }
      } else {
        fail(`${name} missing`);
      }
    });

    // Check dependencies
    if (packageContent.dependencies?.next && packageContent.dependencies?.react) {
      success('Required dependencies installed');
    } else {
      fail('Missing required dependencies');
    }

  } catch (error) {
    fail(`Error reading package.json: ${error.message}`);
  }
}

/**
 * Production readiness tests
 */
function testProductionReadiness() {
  section('✨ PRODUCTION READINESS TESTS');

  const requiredDocs = [
    'PRODUCTION_SETUP.md',
    'PRODUCTION_READY.md',
  ];

  requiredDocs.forEach(doc => {
    const docPath = path.join(ROOT_DIR, doc);
    if (fs.existsSync(docPath)) {
      success(`${doc} exists`);
    } else {
      fail(`${doc} missing`);
    }
  });

  // Check .gitignore
  const gitignorePath = path.join(ROOT_DIR, '.gitignore');
  try {
    const gitignoreContent = fs.readFileSync(gitignorePath, 'utf8');
    const securityTests = [
      { pattern: /.env/, name: 'Environment files ignored' },
      { pattern: /node_modules/, name: 'node_modules ignored' },
      { pattern: /.next/, name: '.next folder ignored' },
    ];

    securityTests.forEach(({ pattern, name }) => {
      if (pattern.test(gitignoreContent)) {
        success(`${name}`);
      } else {
        fail(`${name}`);
      }
    });
  } catch (error) {
    fail(`Error reading .gitignore: ${error.message}`);
  }
}

/**
 * Generate test report
 */
function generateReport() {
  section('📊 TEST REPORT');

  const percentage = totalTests > 0 ? ((passedTests / totalTests) * 100).toFixed(1) : 0;

  log(`\nTotal Tests: ${totalTests}`, 'cyan');
  log(`Passed: ${passedTests}`, 'green');
  log(`Failed: ${failedTests}`, failedTests > 0 ? 'red' : 'green');
  log(`Success Rate: ${percentage}%\n`, percentage === 100 ? 'green' : 'yellow');

  if (failedList.length > 0) {
    log('Failed Tests:', 'red');
    failedList.forEach(test => log(`  • ${test}`, 'red'));
  }

  section('');
  if (failedTests === 0) {
    log('🎉 ALL TESTS PASSED! Production ready.', 'green');
    process.exit(0);
  } else {
    log(`⚠️  ${failedTests} test(s) failed. Please review above.`, 'yellow');
    process.exit(1);
  }
}

/**
 * Run all tests
 */
function runAllTests() {
  log('\n🧪 VOIDLABS AUTOMATED TEST SUITE\n', 'cyan');
  log(`Testing at: ${ROOT_DIR}\n`, 'blue');

  testFileSystem();
  testBuildOutput();
  testSEO();
  testConfiguration();
  testDeployment();
  testPackageConfig();
  testProductionReadiness();

  generateReport();
}

// Run tests
runAllTests();
