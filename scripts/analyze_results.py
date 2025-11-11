#!/usr/bin/env python3
"""
Results Analysis and Reporting
Analyzes test data and generates comprehensive reports
"""

import json
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict


# ============================================================================
# Data Loading
# ============================================================================

def load_results_from_db(db_path: Path) -> List[Dict]:
    """
    Load experiment results from SQLite database

    Args:
        db_path: Path to experiments database

    Returns:
        List of experiment dictionaries
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM experiments
    ORDER BY timestamp DESC
    """)

    results = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return results


# ============================================================================
# Statistical Analysis
# ============================================================================

def analyze_success_rates(results: List[Dict]) -> Dict:
    """
    Calculate success rates by parameter values

    Args:
        results: List of experiment results

    Returns:
        Dictionary of success rates by parameter
    """
    analysis = {}

    # Group by each parameter
    parameters = ['denoise', 'steps', 'motion_scale', 'sampler', 'scheduler']

    for param in parameters:
        param_stats = defaultdict(lambda: {"total": 0, "success": 0})

        for result in results:
            value = result.get(param)
            if value is None:
                continue

            # Round continuous parameters for grouping
            if param in ['denoise', 'motion_scale']:
                value = round(value, 2)

            param_stats[value]["total"] += 1
            if result["success"]:
                param_stats[value]["success"] += 1

        # Calculate success rates
        analysis[param] = {}
        for value, stats in param_stats.items():
            success_rate = stats["success"] / stats["total"] * 100 if stats["total"] > 0 else 0
            analysis[param][value] = {
                "total": stats["total"],
                "success": stats["success"],
                "failed": stats["total"] - stats["success"],
                "success_rate": success_rate
            }

    return analysis


def calculate_avg_duration(results: List[Dict]) -> Dict:
    """
    Calculate average processing duration by parameters

    Args:
        results: List of experiment results

    Returns:
        Dictionary of average durations
    """
    duration_stats = defaultdict(lambda: [])

    for result in results:
        if result["success"] and result.get("duration_seconds"):
            # Group by key parameters
            key = (
                round(result.get("denoise", 0), 2),
                result.get("steps", 0)
            )
            duration_stats[key].append(result["duration_seconds"])

    analysis = {}
    for (denoise, steps), durations in duration_stats.items():
        if durations:
            analysis[f"d{denoise}_st{steps}"] = {
                "denoise": denoise,
                "steps": steps,
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "count": len(durations)
            }

    return analysis


def find_best_configurations(results: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Identify best parameter configurations

    Args:
        results: List of experiment results
        top_n: Number of top configurations to return

    Returns:
        List of best configurations
    """
    # Group by parameter combination
    config_stats = defaultdict(lambda: {
        "total": 0,
        "success": 0,
        "durations": [],
        "params": None
    })

    for result in results:
        # Create config key
        config_key = (
            round(result.get("denoise", 0), 2),
            result.get("steps", 0),
            round(result.get("motion_scale", 0), 1),
            result.get("sampler", ""),
            result.get("scheduler", "")
        )

        stats = config_stats[config_key]
        stats["total"] += 1

        if result["success"]:
            stats["success"] += 1
            if result.get("duration_seconds"):
                stats["durations"].append(result["duration_seconds"])

        if stats["params"] is None:
            stats["params"] = {
                "denoise": result.get("denoise"),
                "steps": result.get("steps"),
                "motion_scale": result.get("motion_scale"),
                "cfg_scale": result.get("cfg_scale"),
                "sampler": result.get("sampler"),
                "scheduler": result.get("scheduler")
            }

    # Calculate scores (success_rate * 0.7 + speed_score * 0.3)
    scored_configs = []
    for config_key, stats in config_stats.items():
        if stats["total"] == 0:
            continue

        success_rate = stats["success"] / stats["total"]
        avg_duration = sum(stats["durations"]) / len(stats["durations"]) if stats["durations"] else 300

        # Normalize duration (0-1, faster is better)
        # Assume 60s is best, 300s is baseline
        speed_score = max(0, min(1, (300 - avg_duration) / 240))

        # Combined score
        overall_score = success_rate * 0.7 + speed_score * 0.3

        scored_configs.append({
            "params": stats["params"],
            "success_rate": success_rate * 100,
            "avg_duration": avg_duration,
            "total_tests": stats["total"],
            "successful_tests": stats["success"],
            "overall_score": overall_score * 100
        })

    # Sort by overall score
    scored_configs.sort(key=lambda x: x["overall_score"], reverse=True)

    return scored_configs[:top_n]


# ============================================================================
# Report Generation
# ============================================================================

def generate_text_summary(results: List[Dict], output_path: Path):
    """
    Generate text summary report

    Args:
        results: List of experiment results
        output_path: Path to save summary.txt
    """
    total_experiments = len(results)
    successful = sum(1 for r in results if r["success"])
    failed = total_experiments - successful

    success_rate_analysis = analyze_success_rates(results)
    duration_analysis = calculate_avg_duration(results)
    best_configs = find_best_configurations(results, top_n=5)

    with open(output_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("COMFYUI AUTOMATED TESTING RESULTS SUMMARY\n")
        f.write("=" * 70 + "\n\n")

        # Overall statistics
        f.write("OVERALL STATISTICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total experiments: {total_experiments}\n")
        f.write(f"Successful: {successful} ({successful/total_experiments*100:.1f}%)\n")
        f.write(f"Failed: {failed} ({failed/total_experiments*100:.1f}%)\n\n")

        # Success rates by denoise
        f.write("SUCCESS RATES BY DENOISE VALUE\n")
        f.write("-" * 70 + "\n")
        if 'denoise' in success_rate_analysis:
            denoise_stats = sorted(success_rate_analysis['denoise'].items())
            for denoise, stats in denoise_stats:
                f.write(f"  {denoise:.2f}: {stats['success_rate']:.1f}% "
                       f"({stats['success']}/{stats['total']} tests)\n")
        f.write("\n")

        # Success rates by steps
        f.write("SUCCESS RATES BY STEPS\n")
        f.write("-" * 70 + "\n")
        if 'steps' in success_rate_analysis:
            steps_stats = sorted(success_rate_analysis['steps'].items())
            for steps, stats in steps_stats:
                f.write(f"  {steps}: {stats['success_rate']:.1f}% "
                       f"({stats['success']}/{stats['total']} tests)\n")
        f.write("\n")

        # Average processing times
        f.write("AVERAGE PROCESSING TIMES\n")
        f.write("-" * 70 + "\n")
        duration_sorted = sorted(
            duration_analysis.items(),
            key=lambda x: x[1]['avg_duration']
        )
        for config_name, stats in duration_sorted[:10]:
            f.write(f"  denoise={stats['denoise']:.2f}, steps={stats['steps']}: "
                   f"{stats['avg_duration']:.1f}s avg "
                   f"({stats['min_duration']:.1f}-{stats['max_duration']:.1f}s range, "
                   f"{stats['count']} tests)\n")
        f.write("\n")

        # Top 5 configurations
        f.write("TOP 5 RECOMMENDED CONFIGURATIONS\n")
        f.write("-" * 70 + "\n")
        for i, config in enumerate(best_configs, 1):
            f.write(f"\n{i}. Overall Score: {config['overall_score']:.1f}/100\n")
            f.write(f"   Parameters:\n")
            for param, value in config['params'].items():
                if value is not None:
                    if isinstance(value, float):
                        f.write(f"     {param}: {value:.2f}\n")
                    else:
                        f.write(f"     {param}: {value}\n")
            f.write(f"   Success rate: {config['success_rate']:.1f}% ")
            f.write(f"({config['successful_tests']}/{config['total_tests']} tests)\n")
            f.write(f"   Avg duration: {config['avg_duration']:.1f}s\n")

        # Recommendations
        f.write("\n" + "=" * 70 + "\n")
        f.write("RECOMMENDATIONS\n")
        f.write("=" * 70 + "\n\n")

        # Find best denoise value
        best_denoise = None
        best_denoise_rate = 0
        if 'denoise' in success_rate_analysis:
            for denoise, stats in success_rate_analysis['denoise'].items():
                if stats['success_rate'] > best_denoise_rate and stats['total'] >= 5:
                    best_denoise = denoise
                    best_denoise_rate = stats['success_rate']

        if best_denoise:
            f.write(f"✅ Use denoise={best_denoise:.2f} for best character preservation\n")
            f.write(f"   ({best_denoise_rate:.1f}% success rate)\n\n")

        # Find best steps value
        best_steps = None
        best_steps_rate = 0
        if 'steps' in success_rate_analysis:
            for steps, stats in success_rate_analysis['steps'].items():
                if stats['success_rate'] > best_steps_rate and stats['total'] >= 5:
                    best_steps = steps
                    best_steps_rate = stats['success_rate']

        if best_steps:
            f.write(f"✅ Use steps={best_steps} for optimal quality/speed balance\n")
            f.write(f"   ({best_steps_rate:.1f}% success rate)\n\n")

        # Warnings
        if 'denoise' in success_rate_analysis:
            for denoise, stats in success_rate_analysis['denoise'].items():
                if stats['success_rate'] < 50 and stats['total'] >= 5:
                    f.write(f"⚠️  Avoid denoise={denoise:.2f} - high failure rate ")
                    f.write(f"({stats['success_rate']:.1f}%)\n")

        f.write("\n" + "=" * 70 + "\n")

    print(f"📄 Text summary saved to: {output_path}")


def generate_html_gallery(results: List[Dict], experiments_dir: Path, output_path: Path):
    """
    Generate HTML gallery of test outputs

    Args:
        results: List of experiment results
        experiments_dir: Directory containing experiment outputs
        output_path: Path to save gallery.html
    """
    # Filter successful results with output files
    successful_results = [r for r in results if r["success"] and r.get("output_file")]

    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>ComfyUI Test Results Gallery</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1e1e1e;
            color: #e0e0e0;
        }
        h1 {
            text-align: center;
            color: #4CAF50;
        }
        .stats {
            text-align: center;
            margin: 20px 0;
            font-size: 18px;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .item {
            background: #2d2d2d;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .item img {
            width: 100%;
            height: auto;
            border-radius: 4px;
            cursor: pointer;
        }
        .item img:hover {
            opacity: 0.8;
        }
        .params {
            margin-top: 10px;
            font-size: 13px;
            line-height: 1.6;
        }
        .param-label {
            color: #9e9e9e;
        }
        .param-value {
            color: #4CAF50;
            font-weight: bold;
        }
        .nft-id {
            font-size: 16px;
            font-weight: bold;
            color: #2196F3;
            margin-bottom: 8px;
        }
        .duration {
            color: #FF9800;
        }
    </style>
</head>
<body>
    <h1>🎨 ComfyUI Test Results Gallery</h1>
    <div class="stats">
        <strong>""" + f"{len(successful_results)}</strong> successful animations generated" + """
    </div>
    <div class="gallery">
"""

    for result in successful_results:
        output_file = Path(result["output_file"])
        if not output_file.exists():
            continue

        # Make path relative to output HTML location
        rel_path = output_file.relative_to(experiments_dir.parent)

        html += f"""
        <div class="item">
            <div class="nft-id">NFT {result['nft_id']}</div>
            <img src="{rel_path}" alt="NFT {result['nft_id']}" onclick="window.open(this.src)">
            <div class="params">
                <div><span class="param-label">Denoise:</span> <span class="param-value">{result.get('denoise', 'N/A'):.2f}</span></div>
                <div><span class="param-label">Steps:</span> <span class="param-value">{result.get('steps', 'N/A')}</span></div>
                <div><span class="param-label">Motion Scale:</span> <span class="param-value">{result.get('motion_scale', 'N/A'):.2f}</span></div>
                <div><span class="param-label">Sampler:</span> <span class="param-value">{result.get('sampler', 'N/A')}</span></div>
                <div><span class="param-label">Scheduler:</span> <span class="param-value">{result.get('scheduler', 'N/A')}</span></div>
                <div class="duration">⏱ {result.get('duration_seconds', 0):.1f}s</div>
            </div>
        </div>
"""

    html += """
    </div>
</body>
</html>
"""

    with open(output_path, 'w') as f:
        f.write(html)

    print(f"🌐 HTML gallery saved to: {output_path}")


def export_csv(results: List[Dict], output_path: Path):
    """
    Export results to CSV for Excel analysis

    Args:
        results: List of experiment results
        output_path: Path to save CSV file
    """
    import csv

    fieldnames = [
        'timestamp', 'batch_id', 'nft_id', 'success',
        'denoise', 'steps', 'motion_scale', 'cfg_scale',
        'sampler', 'scheduler', 'duration_seconds',
        'file_size_bytes', 'error_message'
    ]

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for result in results:
            row = {k: result.get(k, '') for k in fieldnames}
            writer.writerow(row)

    print(f"📊 CSV export saved to: {output_path}")


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Analyze ComfyUI test results and generate reports"
    )

    parser.add_argument(
        "--db",
        type=str,
        required=True,
        help="Path to experiments.db file"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="experiments",
        help="Output directory for reports (default: experiments/)"
    )

    args = parser.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return 1

    output_dir = Path(args.output)
    experiments_dir = output_dir

    print("Loading results from database...")
    results = load_results_from_db(db_path)

    if not results:
        print("❌ No results found in database")
        return 1

    print(f"Found {len(results)} experiment results")

    # Generate reports
    print("\nGenerating reports...")

    summary_path = output_dir / "summary.txt"
    generate_text_summary(results, summary_path)

    gallery_path = output_dir / "gallery.html"
    generate_html_gallery(results, experiments_dir, gallery_path)

    csv_path = output_dir / "results.csv"
    export_csv(results, csv_path)

    print("\n✅ Analysis complete!")
    print(f"\nView results:")
    print(f"  Summary: {summary_path}")
    print(f"  Gallery: {gallery_path}")
    print(f"  CSV: {csv_path}")

    return 0


if __name__ == "__main__":
    exit(main())
