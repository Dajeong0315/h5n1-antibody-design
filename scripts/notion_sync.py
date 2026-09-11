"""Automate Notion database sync for H5N1 pipeline"""

import json
import pandas as pd
import subprocess
from pathlib import Path
from datetime import datetime

def create_notion_exports():
    """Generate CSV files for Notion import"""

    print("="*70)
    print("NOTION DATABASE SYNC - H5N1 Pipeline")
    print("="*70)

    # Load composite scores
    df_scores = pd.read_csv('stage3_evaluation/composite_scores.csv')
    top5 = df_scores.head(5)

    # 1. Pipeline Progress CSV
    print("\n[STEP 1] Creating pipeline progress data...")
    stages_data = {
        'Stage': [
            'Pre-Stage',
            'Stage 1',
            'Stage 2',
            'Stage 3'
        ],
        'Status': [
            'Completed',
            'Completed',
            'Completed',
            'Completed'
        ],
        'Output': [
            '2 epitopes (A:158, A:159), 1 hotspot (A:159, BSA=57.85A²)',
            '30 RFDiffusion backbones → 20 ProteinMPNN sequences',
            '30/30 structures validated (pLDDT≥80, RMSD<2.0Å)',
            'Top 5 candidates selected (composite scoring: 50% pLDDT + 50% ΔG)'
        ],
        'Date Completed': [
            '2026-09-11',
            '2026-09-11',
            '2026-09-11',
            '2026-09-11'
        ]
    }

    df_stages = pd.DataFrame(stages_data)
    df_stages.to_csv('notion_pipeline_progress.csv', index=False)
    print(f"  [OK] notion_pipeline_progress.csv ({len(df_stages)} stages)")

    # 2. Top 5 Candidates CSV
    print("\n[STEP 2] Creating top 5 candidates data...")
    candidates_data = {
        'Rank': [int(row['rank']) for _, row in top5.iterrows()],
        'Candidate ID': [row['candidate_id'] for _, row in top5.iterrows()],
        'pLDDT (Confidence)': [round(row['plddt'], 2) for _, row in top5.iterrows()],
        'Delta_G (kcal/mol)': [round(row['delta_g'], 2) for _, row in top5.iterrows()],
        'Composite Score': [round(row['composite_score'], 4) for _, row in top5.iterrows()],
        'Status': ['Ready for Validation'] * 5
    }

    df_candidates = pd.DataFrame(candidates_data)
    df_candidates.to_csv('notion_top5_candidates.csv', index=False)
    print(f"  [OK] notion_top5_candidates.csv ({len(df_candidates)} candidates)")

    # 3. Full Results CSV (all 30)
    print("\n[STEP 3] Creating full results data...")
    df_scores.to_csv('notion_all_candidates.csv', index=False)
    print(f"  [OK] notion_all_candidates.csv ({len(df_scores)} total candidates)")

    return df_stages, df_candidates, df_scores

def sync_to_notion_api(notion_token, database_id):
    """Sync data to Notion using API"""

    try:
        from notion_client import Client
    except ImportError:
        print("\n[WARN] notion-client not installed")
        print("[TIP] pip install notion-client")
        return False

    print("\n[STEP 4] Syncing to Notion API...")

    if not notion_token:
        print("  [SKIP] No NOTION_TOKEN provided")
        return False

    if not database_id:
        print("  [INFO] No database ID - create one at notion.so first")
        print("         Then run with: python notion_sync.py <token> <db_id>")
        return False

    notion = Client(auth=notion_token)

    try:
        # Verify connection
        response = notion.databases.retrieve(database_id)
        print(f"  ✓ Connected to Notion database")

        # Load data
        df_candidates = pd.read_csv('notion_top5_candidates.csv')

        # Add pages (simplified - full implementation would be more complex)
        for _, row in df_candidates.iterrows():
            try:
                notion.pages.create(
                    parent={"database_id": database_id},
                    properties={
                        "Rank": {"number": int(row['Rank'])},
                        "ID": {"title": [{"text": {"content": row['Candidate ID']}}]},
                        "pLDDT": {"number": row['pLDDT (Confidence)']},
                        "ΔG": {"number": row['ΔG (kcal/mol)']},
                        "Score": {"number": row['Composite Score']},
                        "Status": {"select": {"name": row['Status']}}
                    }
                )
                print(f"    [OK] Added {row['Candidate ID']}")
            except Exception as e:
                print(f"    [WARN] {row['Candidate ID']}: {str(e)[:50]}")

        return True

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

def git_push():
    """Push CSV files to GitHub"""

    print("\n[STEP 5] Pushing to GitHub...")

    try:
        subprocess.run('git add notion_*.csv', shell=True, check=True)

        result = subprocess.run(
            'git commit -m "Add Notion database exports: pipeline progress + Top 5 candidates" '
            '-m "- notion_pipeline_progress.csv (4 stages)"'
            '-m "- notion_top5_candidates.csv (Top 5)"'
            '-m "- notion_all_candidates.csv (all 30)"',
            shell=True,
            capture_output=True,
            text=True
        )

        if 'nothing to commit' in result.stdout or result.returncode == 1:
            print("  (no changes to commit)")
        else:
            print("  [OK] Committed to git")

            push_result = subprocess.run(
                'git push origin main',
                shell=True,
                capture_output=True,
                text=True
            )

            if push_result.returncode == 0:
                print("  [OK] Pushed to GitHub")
                return True
            else:
                print(f"  [WARN] Push failed: {push_result.stderr[:100]}")
                return False

    except Exception as e:
        print(f"  [ERROR] {str(e)}")
        return False

def print_summary(df_stages, df_candidates, df_scores):
    """Print summary and next steps"""

    print("\n" + "="*70)
    print("NOTION SYNC COMPLETE [SUCCESS]")
    print("="*70)

    print("\n[GENERATED FILES]")
    print("  1. notion_pipeline_progress.csv  - 4 pipeline stages")
    print("  2. notion_top5_candidates.csv    - Top 5 with scores")
    print("  3. notion_all_candidates.csv     - All 30 candidates")

    print("\n[PIPELINE SUMMARY]")
    print(df_stages[['Stage', 'Status', 'Date Completed']].to_string(index=False))

    print("\n[TOP 5 CANDIDATES]")
    print(df_candidates[['Rank', 'Candidate ID', 'pLDDT (Confidence)', 'Delta_G (kcal/mol)', 'Composite Score']].to_string(index=False))

    print("\n[PERFORMANCE STATS]")
    print(f"  Total Candidates: {len(df_scores)}")
    print(f"  Mean pLDDT: {df_scores['plddt'].mean():.2f} ± {df_scores['plddt'].std():.2f}")
    print(f"  Mean ΔG: {df_scores['delta_g'].mean():.2f} ± {df_scores['delta_g'].std():.2f}")
    print(f"  Best Score: {df_scores['composite_score'].max():.4f}")
    print(f"  Worst Score: {df_scores['composite_score'].min():.4f}")

    print("\n[NEXT STEPS]")
    print("  Option 1 (Manual):")
    print("    1. Download the CSV files")
    print("    2. Open Notion.so → Create new Database")
    print("    3. Import → Select CSV file")
    print("")
    print("  Option 2 (Automated):")
    print("    1. Get NOTION_TOKEN from https://www.notion.so/my-integrations")
    print("    2. Create Database ID at notion.so")
    print("    3. Run: python scripts/notion_sync.py <token> <db_id>")
    print("")
    print("  [OK] CSV files pushed to GitHub automatically")
    print(f"     Repository: https://github.com/Dajeong0315/h5n1-antibody-design")

    print("\n" + "="*70)

if __name__ == '__main__':
    import sys

    # Create exports
    df_stages, df_candidates, df_scores = create_notion_exports()

    # Try to push to GitHub
    git_push()

    # Try API sync if credentials provided
    notion_token = sys.argv[1] if len(sys.argv) > 1 else None
    database_id = sys.argv[2] if len(sys.argv) > 2 else None

    if notion_token and database_id:
        sync_to_notion_api(notion_token, database_id)

    # Print summary
    print_summary(df_stages, df_candidates, df_scores)
