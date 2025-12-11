#!/bin/bash
#
# Power Laws & Fractals - Project Launcher
#
# Just run: ./start.sh
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

show_menu() {
    clear
    echo ""
    echo -e "${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║${NC}     🔺 ${CYAN}POWER LAWS & FRACTALS${NC} - Veritasium Edition        ${BOLD}║${NC}"
    echo -e "${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}1)${NC}  🐍  Python Demo          ${YELLOW}(recommended start)${NC}"
    echo -e "  ${GREEN}2)${NC}  🐘  PostgreSQL           ${YELLOW}(requires Docker)${NC}"
    echo -e "  ${GREEN}3)${NC}  📓  Jupyter Notebook     ${YELLOW}(interactive analysis)${NC}"
    echo -e "  ${GREEN}4)${NC}  🌐  HTML Visualizer      ${YELLOW}(opens in browser)${NC}"
    echo -e "  ${GREEN}5)${NC}  🐹  Go Demo              ${YELLOW}(requires Go)${NC}"
    echo ""
    echo -e "  ${MAGENTA}s)${NC}  📄  View SSoT JSON       ${YELLOW}(source of truth)${NC}"
    echo -e "  ${MAGENTA}r)${NC}  📖  View README"
    echo -e "  ${MAGENTA}q)${NC}  ❌  Quit"
    echo ""
    echo -e "${BOLD}────────────────────────────────────────────────────────────────${NC}"
    echo -n "  Pick an option: "
}

run_python() {
    echo ""
    echo -e "${CYAN}Running Python tests...${NC}"
    echo ""
    python3 "$SCRIPT_DIR/python/run-tests.py"
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

run_postgres() {
    echo ""
    echo -e "${CYAN}Running PostgreSQL tests...${NC}"
    echo ""
    if command -v psql &> /dev/null; then
        python3 "$SCRIPT_DIR/postgres/run-tests.py"
    else
        echo -e "${YELLOW}psql not found. Install PostgreSQL client tools.${NC}"
        echo -e "On macOS: ${BLUE}brew install libpq${NC}"
        echo -e "See: ${BLUE}postgres/README.md${NC}"
    fi
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

run_jupyter() {
    echo ""
    echo -e "${CYAN}Starting Jupyter Notebook...${NC}"
    echo ""
    cd "$SCRIPT_DIR/jupyter"
    if command -v jupyter &> /dev/null; then
        jupyter notebook power-laws-and-fractals.ipynb
    else
        echo -e "${YELLOW}Jupyter not found. Install with: pip install jupyter${NC}"
        echo -e "Then run: ${BLUE}jupyter notebook jupyter/power-laws-and-fractals.ipynb${NC}"
    fi
    cd "$SCRIPT_DIR"
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

run_visualizer() {
    echo ""
    echo -e "${CYAN}Opening HTML visualizer in browser...${NC}"
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$SCRIPT_DIR/visualizer/index.html"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "$SCRIPT_DIR/visualizer/index.html" 2>/dev/null || echo "Open visualizer/index.html in your browser"
    else
        echo "Open visualizer/index.html in your browser"
    fi
    echo -e "${GREEN}Opened!${NC}"
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

run_golang() {
    echo ""
    echo -e "${CYAN}Running Go demo...${NC}"
    echo ""
    cd "$SCRIPT_DIR/golang"
    if command -v go &> /dev/null; then
        go run rulebook-to-golang.go
    else
        echo -e "${YELLOW}Go not found. Install Go to run this demo.${NC}"
        echo -e "See: ${BLUE}golang/README.md${NC}"
    fi
    cd "$SCRIPT_DIR"
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

view_ssot() {
    echo ""
    echo -e "${CYAN}Source of Truth (first 50 lines):${NC}"
    echo ""
    head -50 "$SCRIPT_DIR/ssot/ERB_veritasium-power-laws-and-fractals.json"
    echo ""
    echo -e "${YELLOW}Full file: ssot/ERB_veritasium-power-laws-and-fractals.json${NC}"
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

view_readme() {
    echo ""
    if command -v less &> /dev/null; then
        less "$SCRIPT_DIR/README.md"
    else
        cat "$SCRIPT_DIR/README.md"
    fi
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Main loop
while true; do
    show_menu
    read -r choice
    
    case $choice in
        1) run_python ;;
        2) run_postgres ;;
        3) run_jupyter ;;
        4) run_visualizer ;;
        5) run_golang ;;
        s|S) view_ssot ;;
        r|R) view_readme ;;
        q|Q) 
            echo ""
            echo -e "${GREEN}Goodbye! 🔺${NC}"
            echo ""
            exit 0 
            ;;
        *) 
            echo -e "${YELLOW}Invalid option. Try again.${NC}"
            sleep 1
            ;;
    esac
done

