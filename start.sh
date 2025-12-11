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
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[1m'
DIM='\033[2m'

show_menu() {
    clear
    echo ""
    echo -e "${BOLD}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║${NC}     🔺 ${CYAN}POWER LAWS & FRACTALS${NC} - Veritasium Edition        ${BOLD}║${NC}"
    echo -e "${BOLD}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BOLD}Test Platforms:${NC}"
    echo -e "  ${GREEN}1)${NC}  🧪  Run All Platform Tests   ${YELLOW}(orchestrator)${NC}"
    echo -e "  ${GREEN}2)${NC}  🐍  Python Tests Only"
    echo -e "  ${GREEN}3)${NC}  🐹  Go Tests Only"
    echo -e "  ${GREEN}4)${NC}  🐘  PostgreSQL Tests Only    ${DIM}(requires Docker)${NC}"
    echo ""
    echo -e "  ${BOLD}Visualizers:${NC}"
    echo -e "  ${GREEN}5)${NC}  🔬  Cross-Platform Comparison"
    echo -e "  ${GREEN}6)${NC}  🌐  Open HTML Dashboard      ${YELLOW}(opens in browser)${NC}"
    echo -e "  ${GREEN}7)${NC}  📊  Generate HTML Report"
    echo ""
    echo -e "  ${BOLD}Utilities:${NC}"
    echo -e "  ${MAGENTA}g)${NC}  🔄  Regenerate Test Data     ${DIM}(from SSoT)${NC}"
    echo -e "  ${MAGENTA}s)${NC}  📄  View SSoT JSON          ${DIM}(source of truth)${NC}"
    echo -e "  ${MAGENTA}r)${NC}  📖  View README"
    echo -e "  ${MAGENTA}j)${NC}  📓  Jupyter Notebook        ${DIM}(interactive analysis)${NC}"
    echo ""
    echo -e "  ${RED}q)${NC}  ❌  Quit"
    echo ""
    echo -e "${BOLD}────────────────────────────────────────────────────────────────${NC}"
    echo -n "  Pick an option: "
}

run_all_tests() {
    echo ""
    echo -e "${CYAN}Running all platform tests via orchestrator...${NC}"
    echo ""
    python3 "$SCRIPT_DIR/orchestrator.py" --all --regenerate
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
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

run_golang() {
    echo ""
    echo -e "${CYAN}Running Go tests...${NC}"
    echo ""
    cd "$SCRIPT_DIR/golang"
    if command -v go &> /dev/null; then
        go run .
    else
        echo -e "${YELLOW}Go not found. Install Go to run this test.${NC}"
        echo -e "See: ${BLUE}golang/README.md${NC}"
    fi
    cd "$SCRIPT_DIR"
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

run_comparison() {
    echo ""
    echo -e "${CYAN}Running cross-platform comparison...${NC}"
    echo ""
    python3 "$SCRIPT_DIR/visualizer/compare.py"
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

open_dashboard() {
    echo ""
    echo -e "${CYAN}Opening HTML dashboard in browser...${NC}"
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

generate_report() {
    echo ""
    echo -e "${CYAN}Generating HTML report...${NC}"
    echo ""
    python3 "$SCRIPT_DIR/visualizer/compare.py" --html
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$SCRIPT_DIR/visualizer/report.html"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "$SCRIPT_DIR/visualizer/report.html" 2>/dev/null
    fi
    echo ""
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

regenerate_data() {
    echo ""
    echo -e "${CYAN}Regenerating test data from SSoT...${NC}"
    echo ""
    python3 "$SCRIPT_DIR/generate-test-data.py"
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
        1) run_all_tests ;;
        2) run_python ;;
        3) run_golang ;;
        4) run_postgres ;;
        5) run_comparison ;;
        6) open_dashboard ;;
        7) generate_report ;;
        g|G) regenerate_data ;;
        s|S) view_ssot ;;
        r|R) view_readme ;;
        j|J) run_jupyter ;;
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
