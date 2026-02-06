#!/bin/bash

# arXiv Researcher - One-Click Installation Script
# Installs the main skill and all sub-skills to ~/.claude/skills/

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="$HOME/.claude/skills"

echo -e "${BLUE}🚀 Installing arXiv Researcher Skills...${NC}"
echo ""

# Create skills directory if it doesn't exist
mkdir -p "$SKILLS_DIR"

# Function to install a skill
install_skill() {
    local name=$1
    local source=$2
    local target="$SKILLS_DIR/$name"

    if [ -d "$target" ]; then
        rm -rf "$target"
    fi

    cp -r "$source" "$target"
    echo -e "${GREEN}✅ Installed $name${NC}"
}

# Install main skill (with scripts/ and assets/)
install_skill "arxiv-researcher" "$SCRIPT_DIR"

# Install sub-skills
SUB_SKILLS=(
    "arxiv-search"
    "arxiv-init"
    "arxiv-daily"
    "arxiv-context"
    "arxiv-read"
    "arxiv-repro"
    "arxiv-lab"
    "arxiv-contrib"
    "arxiv-extend"
)

for skill in "${SUB_SKILLS[@]}"; do
    if [ -d "$SCRIPT_DIR/skills/$skill" ]; then
        install_skill "$skill" "$SCRIPT_DIR/skills/$skill"
    else
        echo -e "${RED}⚠️  Warning: $skill not found in skills/${NC}"
    fi
done

# Configure Knowledge Base Path
echo ""
echo -e "${BLUE}📂 Configuration${NC}"
DEFAULT_PATH="$HOME/knowledge/arxiv"
CONFIG_FILE="$HOME/.arxiv_researcher_config.json"

if [ -f "$CONFIG_FILE" ]; then
    CURRENT_PATH=$(grep -o '"arxiv_root": *"[^"]*"' "$CONFIG_FILE" | cut -d'"' -f4)
    echo -e "Current knowledge base: ${GREEN}$CURRENT_PATH${NC}"
    read -p "Keep this path? [Y/n] " KEEP
    if [[ "$KEEP" =~ ^[Nn]$ ]]; then
        SET_PATH=1
    else
        SET_PATH=0
    fi
else
    SET_PATH=1
fi

if [ "$SET_PATH" -eq 1 ]; then
    echo "Where do you want to store your papers and code?"
    read -p "Path [default: ~/knowledge/arxiv]: " USER_PATH
    USER_PATH=${USER_PATH:-"$DEFAULT_PATH"}

    # Simple tilde expansion for the config file
    if [[ "$USER_PATH" == ~* ]]; then
        USER_PATH="${USER_PATH/#\~/$HOME}"
    fi

    echo "{\"arxiv_root\": \"$USER_PATH\"}" > "$CONFIG_FILE"
    echo -e "${GREEN}✅ Configured knowledge base at: $USER_PATH${NC}"
else
    echo -e "${GREEN}✅ Keeping existing configuration.${NC}"
fi

# Make scripts executable
chmod +x "$SKILLS_DIR/arxiv-researcher/scripts/"*.py 2>/dev/null || true

echo ""
echo -e "${GREEN}🎉 All 10 arXiv skills installed!${NC}"
echo ""
echo "Installed to: $SKILLS_DIR"
echo ""
echo "Skills installed:"
echo "  - arxiv-researcher (main skill)"
for skill in "${SUB_SKILLS[@]}"; do
    echo "  - $skill"
done
echo ""
echo -e "${BLUE}📌 Restart Claude Code to use the new commands.${NC}"
echo ""
echo "Quick start:"
echo "  /arxiv-search speculative decoding"
echo "  /arxiv-init 2401.12345"
echo "  /arxiv-read"
