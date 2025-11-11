#!/usr/bin/env python3
"""
Automated ComfyUI Testing Framework
Complete automation for overnight workflow testing and optimization
"""

import json
import time
import traceback
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("Warning: tqdm not installed. Progress bars disabled.")
    print("Install with: pip install tqdm")

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not installed. Resource monitoring disabled.")
    print("Install with: pip install psutil")

# Import local modules
from comfyui_api import ComfyUIAPI, modify_workflow_params, load_workflow
from generate_test_matrix import (
    generate_phase1_matrix,
    generate_phase2_matrix,
    generate_phase3_matrix,
    load_test_matrix
)


# ============================================================================
# Database Management
# ============================================================================

def init_database(db_path: Path) -> sqlite3.Connection:
    """
    Initialize SQLite database for experiment tracking

    Args:
        db_path: Path to database file

    Returns:
        Database connection
    """
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS experiments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT NOT NULL,
        nft_id TEXT NOT NULL,
        input_image TEXT NOT NULL,
        output_file TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

        -- Workflow parameters
        seed INTEGER,
        steps INTEGER,
        cfg_scale REAL,
        denoise REAL,
        sampler TEXT,
        scheduler TEXT,
        motion_scale REAL,
        context_length INTEGER DEFAULT 16,
        positive_prompt TEXT,
        negative_prompt TEXT,

        -- Execution info
        prompt_id TEXT,
        duration_seconds REAL,
        success BOOLEAN,
        error_message TEXT,

        -- File info
        file_size_bytes INTEGER
    )
    """)

    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_nft_id ON experiments(nft_id);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_batch_id ON experiments(batch_id);
    """)
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_success ON experiments(success);
    """)

    conn.commit()
    return conn


def record_experiment(conn: sqlite3.Connection, experiment_data: Dict):
    """
    Insert experiment result into database

    Args:
        conn: Database connection
        experiment_data: Dictionary with experiment details
    """
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO experiments (
        batch_id, nft_id, input_image, output_file,
        seed, steps, cfg_scale, denoise, sampler, scheduler,
        motion_scale, context_length, positive_prompt, negative_prompt,
        prompt_id, duration_seconds, success, error_message,
        file_size_bytes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        experiment_data["batch_id"],
        experiment_data["nft_id"],
        experiment_data["input_image"],
        experiment_data.get("output_file"),
        experiment_data["seed"],
        experiment_data["steps"],
        experiment_data["cfg_scale"],
        experiment_data["denoise"],
        experiment_data["sampler"],
        experiment_data["scheduler"],
        experiment_data["motion_scale"],
        experiment_data.get("context_length", 16),
        experiment_data.get("positive_prompt", ""),
        experiment_data.get("negative_prompt", ""),
        experiment_data.get("prompt_id"),
        experiment_data.get("duration_seconds"),
        experiment_data["success"],
        experiment_data.get("error_message"),
        experiment_data.get("file_size_bytes"),
    ))

    conn.commit()


# ============================================================================
# Resource Monitoring
# ============================================================================

def check_system_resources(min_memory_gb: float = 2.0, min_disk_gb: float = 5.0) -> bool:
    """
    Check if system has sufficient resources

    Args:
        min_memory_gb: Minimum free memory required (GB)
        min_disk_gb: Minimum free disk space required (GB)

    Returns:
        True if resources are sufficient

    Raises:
        ResourceWarning if resources are low
    """
    if not HAS_PSUTIL:
        return True  # Skip check if psutil not available

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    free_memory_gb = memory.available / (1024**3)
    free_disk_gb = disk.free / (1024**3)

    if free_memory_gb < min_memory_gb:
        raise ResourceWarning(
            f"Low memory: {free_memory_gb:.1f}GB free "
            f"(minimum {min_memory_gb}GB required)"
        )

    if free_disk_gb < min_disk_gb:
        raise ResourceWarning(
            f"Low disk space: {free_disk_gb:.1f}GB free "
            f"(minimum {min_disk_gb}GB required)"
        )

    return True


# ============================================================================
# Checkpoint Management
# ============================================================================

def save_checkpoint(checkpoint_path: Path, batch_id: str, completed_idx: int):
    """
    Save progress checkpoint for resume capability

    Args:
        checkpoint_path: Path to checkpoint file
        batch_id: Current batch identifier
        completed_idx: Index of last completed test
    """
    checkpoint_data = {
        "batch_id": batch_id,
        "completed_idx": completed_idx,
        "timestamp": datetime.now().isoformat()
    }

    with open(checkpoint_path, 'w') as f:
        json.dump(checkpoint_data, f, indent=2)


def load_checkpoint(checkpoint_path: Path) -> Optional[Dict]:
    """
    Load progress checkpoint

    Args:
        checkpoint_path: Path to checkpoint file

    Returns:
        Checkpoint data or None if not found
    """
    if not checkpoint_path.exists():
        return None

    with open(checkpoint_path, 'r') as f:
        return json.load(f)


# ============================================================================
# Single Experiment Execution
# ============================================================================

def run_single_experiment(
    api: ComfyUIAPI,
    workflow_template: Dict,
    params: Dict,
    config: Dict
) -> Tuple[bool, Dict]:
    """
    Run single experiment with retry logic

    Args:
        api: ComfyUI API client
        workflow_template: Base workflow dictionary
        params: Parameters to inject
        config: Configuration dictionary

    Returns:
        (success: bool, result_dict: Dict)
    """
    max_retries = config.get("max_retries", 3)
    retry_delay = config.get("retry_delay_base", 2.0)

    for attempt in range(max_retries):
        try:
            # Modify workflow with test parameters
            workflow = modify_workflow_params(workflow_template, params)

            # Queue workflow
            prompt_id = api.queue_prompt(workflow)

            # Track execution
            success, duration = api.track_execution(prompt_id, timeout=600)

            if not success:
                raise Exception("Execution did not complete successfully")

            # Get output files
            output_files = api.get_output_files(prompt_id)

            if not output_files:
                raise Exception("No output files generated")

            return True, {
                "prompt_id": prompt_id,
                "duration": duration,
                "output_files": output_files,
                "success": True,
                "error": None
            }

        except Exception as e:
            error_msg = str(e)

            if attempt == max_retries - 1:
                # Final attempt failed
                return False, {
                    "success": False,
                    "error": error_msg,
                    "traceback": traceback.format_exc()
                }

            # Retry with exponential backoff
            delay = retry_delay * (2 ** attempt)
            print(f"  Attempt {attempt + 1}/{max_retries} failed: {error_msg}")
            print(f"  Retrying in {delay:.1f} seconds...")
            time.sleep(delay)

    return False, {"success": False, "error": "Max retries exceeded"}


# ============================================================================
# Batch Experiment Runner
# ============================================================================

def run_experiment_batch(
    nft_list: List[str],
    test_matrix: List[Dict],
    config: Dict
) -> Tuple[List[Dict], List[Dict]]:
    """
    Run batch of experiments with full automation

    Args:
        nft_list: List of NFT IDs to test
        test_matrix: List of parameter combinations
        config: Configuration dictionary

    Returns:
        (results, errors)
    """
    # Setup
    batch_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(config["output_dir"]) / batch_id
    output_dir.mkdir(parents=True, exist_ok=True)

    db_path = Path(config["database"])
    conn = init_database(db_path)

    workflow_template = load_workflow(Path(config["base_workflow"]))
    api = ComfyUIAPI(config["comfyui_server"])

    checkpoint_path = Path(config.get("checkpoint_file", "progress_checkpoint.json"))

    # Check for resume
    checkpoint = load_checkpoint(checkpoint_path)
    start_idx = 0
    if checkpoint and checkpoint["batch_id"] == batch_id:
        start_idx = checkpoint["completed_idx"] + 1
        print(f"📂 Resuming from checkpoint: {start_idx} completed")

    total_tests = len(nft_list) * len(test_matrix)
    print(f"\n{'=' * 70}")
    print(f"BATCH {batch_id}")
    print(f"{'=' * 70}")
    print(f"NFTs: {len(nft_list)}")
    print(f"Parameter combinations: {len(test_matrix)}")
    print(f"Total tests: {total_tests}")
    print(f"Output directory: {output_dir}")
    print(f"{'=' * 70}\n")

    results = []
    errors = []

    # Progress bar
    if HAS_TQDM:
        pbar = tqdm(total=total_tests, initial=start_idx, desc="Running experiments")
    else:
        pbar = None

    test_idx = 0
    for nft_idx, nft_id in enumerate(nft_list):
        for param_idx, params in enumerate(test_matrix):
            if test_idx < start_idx:
                test_idx += 1
                continue

            # Resource check
            if test_idx % config.get("resource_check_interval", 10) == 0:
                try:
                    check_system_resources(
                        min_memory_gb=config.get("min_free_memory_gb", 2.0),
                        min_disk_gb=config.get("min_free_disk_gb", 5.0)
                    )
                except ResourceWarning as e:
                    print(f"\n⚠️  {e}")
                    print("Pausing for 60 seconds...")
                    time.sleep(60)

            # Prepare parameters
            full_params = {
                **params,
                "input_image": f"{nft_id}.png",
                "positive_prompt": config.get(
                    "default_positive_prompt",
                    "high quality, pepe frog character, detailed, colorful, meme art, "
                    "(animated:1.2), subtle motion, smooth animation"
                ),
                "negative_prompt": config.get(
                    "default_negative_prompt",
                    "deformed, distorted, disfigured, bad anatomy, wrong colors, "
                    "extra limbs, mutation, flickering, temporal inconsistency"
                )
            }

            # Run experiment
            print(f"\n[{test_idx+1}/{total_tests}] NFT {nft_id} | " +
                  f"denoise={params.get('denoise', 'N/A'):.2f} " +
                  f"steps={params.get('steps', 'N/A')}")

            success, result = run_single_experiment(api, workflow_template, full_params, config)

            if success:
                # Save output file
                output_filename = (
                    f"{nft_id}_"
                    f"s{params['seed']}_"
                    f"d{params['denoise']:.2f}_"
                    f"st{params['steps']}_"
                    f"m{params.get('motion_scale', 1.0):.1f}.gif"
                )
                output_path = output_dir / output_filename

                with open(output_path, 'wb') as f:
                    f.write(result['output_files'][0]['data'])

                # Save metadata sidecar
                metadata_path = output_path.with_suffix('.json')
                metadata = {
                    "nft_id": nft_id,
                    "parameters": params,
                    "execution": {
                        "prompt_id": result["prompt_id"],
                        "duration_seconds": result["duration"],
                        "timestamp": datetime.now().isoformat()
                    },
                    "output": {
                        "file": str(output_path),
                        "size_bytes": output_path.stat().st_size
                    }
                }
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)

                # Record in database
                experiment_data = {
                    "batch_id": batch_id,
                    "nft_id": nft_id,
                    "input_image": full_params["input_image"],
                    "output_file": str(output_path),
                    "seed": params["seed"],
                    "steps": params["steps"],
                    "cfg_scale": params.get("cfg_scale", 7.0),
                    "denoise": params["denoise"],
                    "sampler": params["sampler"],
                    "scheduler": params["scheduler"],
                    "motion_scale": params.get("motion_scale", 1.0),
                    "context_length": 16,
                    "positive_prompt": full_params["positive_prompt"],
                    "negative_prompt": full_params["negative_prompt"],
                    "prompt_id": result["prompt_id"],
                    "duration_seconds": result["duration"],
                    "success": True,
                    "error_message": None,
                    "file_size_bytes": output_path.stat().st_size,
                }

                record_experiment(conn, experiment_data)
                results.append(experiment_data)

                print(f"  ✅ Success | {result['duration']:.1f}s | {output_path.name}")

            else:
                # Log error
                error_data = {
                    "batch_id": batch_id,
                    "nft_id": nft_id,
                    "params": params,
                    "error": result["error"]
                }
                errors.append(error_data)

                # Record failure in database
                experiment_data = {
                    "batch_id": batch_id,
                    "nft_id": nft_id,
                    "input_image": full_params["input_image"],
                    "output_file": None,
                    "seed": params["seed"],
                    "steps": params["steps"],
                    "cfg_scale": params.get("cfg_scale", 7.0),
                    "denoise": params["denoise"],
                    "sampler": params["sampler"],
                    "scheduler": params["scheduler"],
                    "motion_scale": params.get("motion_scale", 1.0),
                    "context_length": 16,
                    "positive_prompt": full_params["positive_prompt"],
                    "negative_prompt": full_params["negative_prompt"],
                    "prompt_id": None,
                    "duration_seconds": None,
                    "success": False,
                    "error_message": result["error"],
                    "file_size_bytes": None,
                }

                record_experiment(conn, experiment_data)

                print(f"  ❌ Failed | {result['error']}")

            # Update progress
            if pbar:
                pbar.update(1)

            # Save checkpoint
            save_checkpoint(checkpoint_path, batch_id, test_idx)

            test_idx += 1

    if pbar:
        pbar.close()

    # Cleanup
    api.close_websocket()
    conn.close()

    # Summary
    print(f"\n{'=' * 70}")
    print("BATCH COMPLETE")
    print(f"{'=' * 70}")
    print(f"Successful: {len(results)}/{total_tests} ({len(results)/total_tests*100:.1f}%)")
    print(f"Failed: {len(errors)}/{total_tests} ({len(errors)/total_tests*100:.1f}%)")
    print(f"Output directory: {output_dir}")
    print(f"Database: {db_path}")
    print(f"{'=' * 70}\n")

    return results, errors


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Automated ComfyUI workflow testing framework"
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config_testing.json",
        help="Configuration file path"
    )

    parser.add_argument(
        "--phase",
        type=int,
        choices=[1, 2, 3],
        help="Run specific testing phase"
    )

    parser.add_argument(
        "--matrix",
        type=str,
        help="Custom test matrix JSON file"
    )

    parser.add_argument(
        "--nfts",
        type=str,
        help="Comma-separated list of NFT IDs to test"
    )

    parser.add_argument(
        "--all-phases",
        action="store_true",
        help="Run all testing phases sequentially"
    )

    args = parser.parse_args()

    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("Create config_testing.json first or specify --config")
        return 1

    with open(config_path, 'r') as f:
        config = json.load(f)

    # Determine NFT list
    if args.nfts:
        nft_list = args.nfts.split(',')
    else:
        # Default: use all NFTs in input directory
        input_dir = Path(config["input_dir"])
        nft_list = [
            f.stem.replace("nft_", "")
            for f in input_dir.glob("*.png")
        ]

        if not nft_list:
            print(f"❌ No NFT images found in {input_dir}")
            print("Add test NFTs to input_test_nfts/ directory")
            return 1

    print(f"NFTs to test: {nft_list}")

    # Determine test matrix
    if args.matrix:
        # Load custom matrix
        test_matrix = load_test_matrix(Path(args.matrix))
        print(f"Loaded custom test matrix: {len(test_matrix)} combinations")
    elif args.phase:
        # Generate phase-specific matrix
        if args.phase == 1:
            test_matrix = generate_phase1_matrix()
        elif args.phase == 2:
            test_matrix = generate_phase2_matrix()
        else:
            test_matrix = generate_phase3_matrix()
    elif args.all_phases:
        print("Running all phases sequentially...")
        # TODO: Implement all-phases logic
        print("❌ --all-phases not yet implemented")
        return 1
    else:
        print("❌ Must specify --phase, --matrix, or --all-phases")
        return 1

    # Run experiments
    try:
        results, errors = run_experiment_batch(nft_list, test_matrix, config)

        print("\n✅ Automation complete!")
        print(f"Analyze results with: python3 scripts/analyze_results.py")

        return 0

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        print("Progress saved. Resume with same command.")
        return 130

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
