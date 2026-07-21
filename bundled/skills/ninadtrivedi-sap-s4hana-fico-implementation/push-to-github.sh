#!/bin/bash

echo "========================================="
echo "SAP S/4HANA FICO Skill - GitHub Push"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "SKILL.md" ]; then
    echo "❌ Error: SKILL.md not found. Please run this script from the sap-s4hana-fico-implementation folder."
    exit 1
fi

# Configure git
echo "⚙️  Configuring git..."
git config --global user.name "ninadtrivedi-finance"
git config --global user.email "ninadtrivedii@gmail.com"

# Initialize repository
echo "📦 Initializing git repository..."
git init

# Add all files
echo "📝 Staging all files..."
git add .

# Create commit
echo "💾 Creating initial commit..."
git commit -m "feat: initial release - SAP S/4HANA FICO Implementation Skill

Complete production-ready skill covering:
- All FI modules (GL, AP, AR, AA, BL, TR) - 6 files
- All CO modules (Cost Centers, Internal Orders, CO-PA, Product Costing, Profit Centers) - 5 files
- SAP-native integrations (MM-FI, SD-FI, PP-CO, PS-FI, HR-FI) - 5 files
- External integrations (Banking, Treasury, Tax) - 3 files
- Country localizations (India, USA, Germany, UK, China, France, Japan, Brazil, Canada, Australia) - 10 files
- Testing guides (Unit, Integration) - 2 files

Features:
- Dual-persona adaptive guidance (fresher teaching + professional expert)
- SPRO paths, transaction codes, IMG activities, config tables
- Field-level guidance with examples
- 4,000+ lines of professional content
- 85KB packaged .skill file

Ready for immediate deployment in SAP implementation projects."

# Set main branch
echo "🌿 Setting main branch..."
git branch -M main

# Add remote
echo ""
echo "🔗 Adding GitHub remote..."
echo "Repository: https://github.com/ninadtrivedi-finance/sap-s4hana-fico-implementation.git"
git remote add origin https://github.com/ninadtrivedi-finance/sap-s4hana-fico-implementation.git

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
echo ""
echo "You will be prompted for credentials:"
echo "  Username: ninadtrivedi-finance"
echo "  Password: [Your Personal Access Token - starts with ghp_]"
echo ""
git push -u origin main

echo ""
echo "========================================="
echo "✅ Done! Repository pushed to GitHub"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Visit: https://github.com/ninadtrivedi-finance/sap-s4hana-fico-implementation"
echo "2. Create a release (tag: v1.0.0)"
echo "3. Attach sap-s4hana-fico-implementation.skill to the release"
echo "4. Share with SAP community!"
echo ""
