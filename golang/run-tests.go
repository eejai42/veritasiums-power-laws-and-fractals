// Power Laws & Fractals - Go Test Runner
//
// Follows the unified testing protocol:
// 1. Load base-data.json (for systems configuration)
// 2. Load test-input.json (raw facts only)
// 3. Compute derived values for test scales
// 4. Output results to test-results/golang-results.json
// 5. Validate against answer-key.json

package main

import (
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"time"

	"erb-power-laws/pkg/rulebook"
)

// ANSI colors
const (
	green  = "\033[92m"
	yellow = "\033[93m"
	cyan   = "\033[96m"
	red    = "\033[91m"
	dim    = "\033[2m"
	reset  = "\033[0m"
	bold   = "\033[1m"
)

func main() {
	// Find project root (parent of golang directory)
	execPath, _ := os.Getwd()
	projectRoot := filepath.Dir(execPath)
	
	// If we're already at project root (golang is a subdirectory)
	if _, err := os.Stat(filepath.Join(execPath, "test-data")); err == nil {
		projectRoot = execPath
	}
	
	// Paths
	testDataDir := filepath.Join(projectRoot, "test-data")
	testResultsDir := filepath.Join(projectRoot, "test-results")
	
	baseDataPath := filepath.Join(testDataDir, "base-data.json")
	testInputPath := filepath.Join(testDataDir, "test-input.json")
	answerKeyPath := filepath.Join(testDataDir, "answer-key.json")
	resultsPath := filepath.Join(testResultsDir, "golang-results.json")
	
	// Ensure results directory exists
	os.MkdirAll(testResultsDir, 0755)
	
	// Load base data
	baseData, err := rulebook.LoadBaseData(baseDataPath)
	if err != nil {
		fmt.Printf("%sError: Could not load base-data.json: %v%s\n", red, err, reset)
		os.Exit(1)
	}
	
	// Load test input
	testInput, err := rulebook.LoadTestInput(testInputPath)
	if err != nil {
		fmt.Printf("%sError: Could not load test-input.json: %v%s\n", red, err, reset)
		os.Exit(1)
	}
	
	// Load answer key
	answerKey, err := rulebook.LoadAnswerKey(answerKeyPath)
	if err != nil {
		fmt.Printf("%sError: Could not load answer-key.json: %v%s\n", red, err, reset)
		os.Exit(1)
	}
	
	// Build systems map
	systemsMap := rulebook.BuildSystemsMap(baseData.Systems)
	
	// Compute derived values for test scales
	computedScales := make([]map[string]interface{}, 0, len(testInput.Scales))
	
	for i := range testInput.Scales {
		scale := &testInput.Scales[i]
		scale.CalculateAllFields(systemsMap)
		computedScales = append(computedScales, scale.ToOutputMap())
	}
	
	// Save results
	results := &rulebook.TestResults{
		Platform:  "golang",
		Timestamp: time.Now().UTC().Format(time.RFC3339),
		Scales:    computedScales,
	}
	
	err = rulebook.SaveResults(resultsPath, results)
	if err != nil {
		fmt.Printf("%sError: Could not save results: %v%s\n", red, err, reset)
		os.Exit(1)
	}
	
	// Validate against answer key
	passCount, failCount, failures := rulebook.ValidateAllScales(computedScales, answerKey)
	
	// Print console output
	printConsoleOutput(systemsMap, computedScales, passCount, failCount, failures)
	
	// Exit with appropriate code
	if failCount > 0 {
		os.Exit(1)
	}
}

func printConsoleOutput(systems rulebook.SystemsMap, computedScales []map[string]interface{}, 
	passCount, failCount int, failures []rulebook.ValidationResult) {
	
	fmt.Printf("\n%s%s\n", bold, "======================================================================")
	fmt.Printf("  %s🐹 POWER LAWS & FRACTALS - Go Test Runner%s\n", bold, reset)
	fmt.Printf("%s======================================================================%s\n", bold, reset)
	
	// Group scales by system
	bySystem := make(map[string][]map[string]interface{})
	for _, scale := range computedScales {
		systemID := scale["System"].(string)
		bySystem[systemID] = append(bySystem[systemID], scale)
	}
	
	// Get sorted system IDs
	systemIDs := make([]string, 0, len(bySystem))
	for id := range bySystem {
		systemIDs = append(systemIDs, id)
	}
	sort.Strings(systemIDs)
	
	fmt.Printf("\n%sComputed Values for Test Scales:%s\n", cyan, reset)
	fmt.Println("──────────────────────────────────────────────────────────────────────")
	
	for _, systemID := range systemIDs {
		scales := bySystem[systemID]
		system := systems[systemID]
		
		icon := "📈"
		if system != nil && system.Class == "fractal" {
			icon = "🔺"
		}
		
		displayName := systemID
		if system != nil {
			displayName = system.DisplayName
		}
		
		fmt.Printf("\n%s %s%s%s\n", icon, bold, displayName, reset)
		fmt.Println("  Iter      Measure        Scale   LogScale   LogMeasure")
		fmt.Println("  ------------------------------------------------------")
		
		// Sort by iteration
		sort.Slice(scales, func(i, j int) bool {
			return scales[i]["Iteration"].(int) < scales[j]["Iteration"].(int)
		})
		
		for _, s := range scales {
			fmt.Printf("  %4d %12.6f %12.8f %10.5f %12.5f\n",
				s["Iteration"].(int),
				s["Measure"].(float64),
				s["Scale"].(float64),
				s["LogScale"].(float64),
				s["LogMeasure"].(float64))
		}
	}
	
	// Validation results
	fmt.Printf("\n%sValidation Results:%s\n", cyan, reset)
	fmt.Println("──────────────────────────────────────────────────────────────────────")
	
	if failCount == 0 {
		fmt.Printf("  %s✓ All %d scales validated successfully!%s\n", green, passCount, reset)
	} else {
		fmt.Printf("  %s⚠ %d passed, %d failed%s\n", yellow, passCount, failCount, reset)
		for i, failure := range failures {
			if i >= 5 {
				break
			}
			fmt.Printf("    • %s:\n", failure.ScaleID)
			for _, m := range failure.Mismatches {
				fmt.Printf("      - %s\n", m)
			}
		}
	}
	
	fmt.Printf("\n%s======================================================================%s\n", bold, reset)
	fmt.Printf("  %s✓ Go test run complete!%s\n", green, reset)
	fmt.Printf("%s======================================================================%s\n\n", bold, reset)
}

