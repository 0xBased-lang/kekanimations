#!/usr/bin/env python3
"""
Test Matrix Generator
Creates systematic testing strategies for ComfyUI workflow optimization
"""

import json
import random
import itertools
from typing import Dict, List, Any
from pathlib import Path


def generate_lhs_matrix(param_ranges: Dict, n_samples: int = 50) -> List[Dict]:
    """
    Generate Latin Hypercube Sampling test matrix

    Latin Hypercube provides good coverage of parameter space with fewer samples
    than full factorial design.

    Args:
        param_ranges: Dictionary of parameter ranges
            Example:
            {
                "denoise": (0.30, 0.60),  # (min, max) for continuous
                "steps": [12, 15, 20, 25],  # list for discrete
                "sampler": ["euler", "dpmpp_2m"]  # list for categorical
            }
        n_samples: Number of test combinations to generate

    Returns:
        List of parameter dictionaries
    """
    try:
        from scipy.stats import qmc
        use_scipy = True
    except ImportError:
        print("Warning: scipy not installed, using simple random sampling instead")
        print("Install scipy for true Latin Hypercube: pip install scipy")
        use_scipy = False

    # Separate parameter types
    continuous_params = []
    continuous_ranges = []
    discrete_params = {}
    categorical_params = {}

    for param, values in param_ranges.items():
        if isinstance(values, tuple) and len(values) == 2:
            # Continuous parameter (min, max)
            continuous_params.append(param)
            continuous_ranges.append(values)
        elif isinstance(values, list):
            if all(isinstance(v, (int, float)) for v in values):
                # Discrete numerical parameter
                discrete_params[param] = values
            else:
                # Categorical parameter
                categorical_params[param] = values

    # Generate Latin Hypercube samples for continuous parameters
    if continuous_params:
        if use_scipy:
            # True Latin Hypercube using scipy
            sampler = qmc.LatinHypercube(d=len(continuous_params))
            lhs_samples = sampler.random(n=n_samples)

            # Scale to actual ranges
            scaled_samples = []
            for sample in lhs_samples:
                scaled = {}
                for i, param in enumerate(continuous_params):
                    min_val, max_val = continuous_ranges[i]
                    scaled[param] = min_val + sample[i] * (max_val - min_val)
                scaled_samples.append(scaled)
        else:
            # Simple random sampling fallback
            scaled_samples = []
            for _ in range(n_samples):
                scaled = {}
                for i, param in enumerate(continuous_params):
                    min_val, max_val = continuous_ranges[i]
                    scaled[param] = random.uniform(min_val, max_val)
                scaled_samples.append(scaled)
    else:
        scaled_samples = [{} for _ in range(n_samples)]

    # Add discrete and categorical parameters
    test_matrix = []
    for sample in scaled_samples:
        test = dict(sample)

        # Add discrete parameters (random choice)
        for param, values in discrete_params.items():
            test[param] = random.choice(values)

        # Add categorical parameters (random choice)
        for param, values in categorical_params.items():
            test[param] = random.choice(values)

        # Generate unique seed for each test
        test["seed"] = random.randint(0, 4294967295)

        test_matrix.append(test)

    return test_matrix


def generate_factorial_matrix(param_grid: Dict) -> List[Dict]:
    """
    Generate full factorial test matrix

    Tests all possible combinations of parameters. Use with narrowed
    parameter ranges to avoid combinatorial explosion.

    Args:
        param_grid: Dictionary of parameter values to test
            Example:
            {
                "denoise": [0.40, 0.45, 0.50],
                "steps": [15, 20],
                "motion_scale": [1.0, 1.2]
            }

    Returns:
        List of parameter dictionaries
    """
    keys = list(param_grid.keys())
    values = [param_grid[k] for k in keys]

    test_matrix = []
    for combination in itertools.product(*values):
        test = dict(zip(keys, combination))
        # Generate unique seed for each test
        test["seed"] = random.randint(0, 4294967295)
        test_matrix.append(test)

    return test_matrix


def generate_phase1_matrix() -> List[Dict]:
    """
    Phase 1: Broad Exploration (Latin Hypercube)

    Tests wide parameter ranges to identify promising regions.
    50 tests × 1 NFT = 50 total runs (~3-4 hours)

    Returns:
        List of 50 diverse parameter combinations
    """
    param_ranges = {
        # Critical parameter: character preservation vs motion
        "denoise": (0.30, 0.60),

        # Quality vs speed trade-off
        "steps": [12, 15, 20, 25],

        # Animation intensity
        "motion_scale": (0.8, 1.5),

        # Prompt adherence
        "cfg_scale": (6.0, 8.0),

        # Sampler selection
        "sampler": ["euler", "dpmpp_2m", "dpmpp_sde"],

        # Scheduler selection
        "scheduler": ["normal", "karras", "exponential"],
    }

    test_matrix = generate_lhs_matrix(param_ranges, n_samples=50)

    print("✅ Phase 1 Test Matrix Generated")
    print(f"   Total combinations: {len(test_matrix)}")
    print(f"   Estimated time: 3-4 hours (1 NFT × 50 tests × ~4 min each)")

    return test_matrix


def generate_phase2_matrix(phase1_results: Dict = None) -> List[Dict]:
    """
    Phase 2: Focused Factorial Testing

    Narrows ranges based on Phase 1 results (if provided) or uses
    reasonable defaults. Tests main effects and interactions.

    24 combinations × 5 NFTs = 120 total runs (~8-10 hours)

    Args:
        phase1_results: Optional analysis results from Phase 1 to inform ranges

    Returns:
        List of 24 focused parameter combinations
    """
    # Default focused ranges (update based on Phase 1 results)
    param_grid = {
        "denoise": [0.40, 0.45, 0.50],      # Narrowed from (0.30-0.60)
        "steps": [15, 20],                   # Narrowed from [12,15,20,25]
        "motion_scale": [1.0, 1.2],         # Narrowed from (0.8-1.5)
        "cfg_scale": [7.0],                  # Fixed at likely optimal
        "sampler": ["dpmpp_2m", "dpmpp_sde"],  # Best 2 from Phase 1
        "scheduler": ["karras"],             # Best 1 from Phase 1
    }

    # If Phase 1 results provided, adjust ranges
    if phase1_results:
        # TODO: Implement adaptive range selection based on Phase 1 success rates
        pass

    test_matrix = generate_factorial_matrix(param_grid)

    print("✅ Phase 2 Test Matrix Generated")
    print(f"   Total combinations: {len(test_matrix)}")
    print(f"   Test with 5 NFTs each = {len(test_matrix) * 5} total runs")
    print(f"   Estimated time: 8-10 hours")

    return test_matrix


def generate_phase3_matrix(best_configs: List[Dict] = None) -> List[Dict]:
    """
    Phase 3: Validation Across NFT Types

    Tests best configurations from Phase 2 across diverse NFT collection.
    3 configs × 20 NFTs = 60 total runs (~5-6 hours)

    Args:
        best_configs: Top 3 parameter sets from Phase 2

    Returns:
        List of 3 best configurations (to test with 20 diverse NFTs)
    """
    if best_configs is None:
        # Default best configurations (update from Phase 2 results)
        best_configs = [
            {
                "name": "Safe & Fast",
                "denoise": 0.40,
                "steps": 15,
                "motion_scale": 1.0,
                "cfg_scale": 7.0,
                "sampler": "dpmpp_2m",
                "scheduler": "karras",
            },
            {
                "name": "Balanced",
                "denoise": 0.45,
                "steps": 20,
                "motion_scale": 1.0,
                "cfg_scale": 7.0,
                "sampler": "dpmpp_2m",
                "scheduler": "karras",
            },
            {
                "name": "High Motion",
                "denoise": 0.50,
                "steps": 20,
                "motion_scale": 1.2,
                "cfg_scale": 7.0,
                "sampler": "dpmpp_sde",
                "scheduler": "karras",
            },
        ]

    # Add unique seeds
    for config in best_configs:
        config["seed"] = random.randint(0, 4294967295)

    print("✅ Phase 3 Test Matrix Generated")
    print(f"   Configurations to validate: {len(best_configs)}")
    print(f"   Test with 20 diverse NFTs each = {len(best_configs) * 20} total runs")
    print(f"   Estimated time: 5-6 hours")

    return best_configs


def save_test_matrix(test_matrix: List[Dict], output_path: Path, phase_name: str = ""):
    """
    Save test matrix to JSON file

    Args:
        test_matrix: List of parameter dictionaries
        output_path: Path to save JSON file
        phase_name: Optional phase identifier
    """
    output_data = {
        "phase": phase_name,
        "total_tests": len(test_matrix),
        "test_matrix": test_matrix,
    }

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"💾 Test matrix saved to: {output_path}")


def load_test_matrix(input_path: Path) -> List[Dict]:
    """
    Load test matrix from JSON file

    Args:
        input_path: Path to JSON file

    Returns:
        List of parameter dictionaries
    """
    with open(input_path, 'r') as f:
        data = json.load(f)

    return data.get("test_matrix", [])


def print_matrix_summary(test_matrix: List[Dict]):
    """
    Print summary statistics of test matrix

    Args:
        test_matrix: List of parameter dictionaries
    """
    print("\n" + "=" * 60)
    print("TEST MATRIX SUMMARY")
    print("=" * 60)

    print(f"Total combinations: {len(test_matrix)}")

    # Analyze parameter distributions
    param_stats = {}
    for test in test_matrix:
        for param, value in test.items():
            if param not in param_stats:
                param_stats[param] = []
            param_stats[param].append(value)

    print("\nParameter Coverage:")
    for param, values in param_stats.items():
        if isinstance(values[0], (int, float)) and param != "seed":
            unique_vals = set(values)
            if len(unique_vals) > 10:
                # Continuous parameter - show range
                print(f"  {param}: {min(values):.3f} - {max(values):.3f}")
            else:
                # Discrete parameter - show values
                print(f"  {param}: {sorted(unique_vals)}")
        elif param != "seed":
            # Categorical parameter
            unique_vals = set(values)
            print(f"  {param}: {unique_vals}")

    print("=" * 60 + "\n")


# Command-line interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate test matrices for ComfyUI workflow optimization")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3], required=True,
                        help="Testing phase to generate")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON file (default: test_matrix_phaseN.json)")
    parser.add_argument("--summary", action="store_true",
                        help="Print detailed summary of generated matrix")

    args = parser.parse_args()

    # Generate test matrix
    if args.phase == 1:
        test_matrix = generate_phase1_matrix()
        default_output = "test_matrix_phase1.json"
    elif args.phase == 2:
        test_matrix = generate_phase2_matrix()
        default_output = "test_matrix_phase2.json"
    else:  # phase == 3
        test_matrix = generate_phase3_matrix()
        default_output = "test_matrix_phase3.json"

    # Save to file
    output_path = Path(args.output or default_output)
    save_test_matrix(test_matrix, output_path, phase_name=f"Phase {args.phase}")

    # Print summary if requested
    if args.summary:
        print_matrix_summary(test_matrix)

    print(f"\n✅ Phase {args.phase} test matrix ready!")
    print(f"   Use with: python3 automated_testing.py --matrix {output_path}")
