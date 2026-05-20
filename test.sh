#!/bin/bash

# VOIDLABS - Automated Test Script
# This script runs the complete test suite

echo ""
echo "=========================================================="
echo "  VOIDLABS - AUTOMATED TEST SUITE"
echo "=========================================================="
echo ""

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "[INFO] Node.js found. Starting tests..."
echo ""

# Run the test suite
node scripts/test.js

# Check test result
if [ $? -eq 0 ]; then
    echo ""
    echo "[SUCCESS] All tests passed! Ready for deployment."
    echo ""
else
    echo ""
    echo "[FAILURE] Some tests failed. Review the output above."
    echo ""
    exit 1
fi
