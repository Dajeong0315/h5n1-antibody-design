# H5N1 Antibody Design Pipeline

Computational pipeline for designing broadly neutralizing antibodies against H5N1 influenza hemagglutinin (HA), using deep learning (RFDiffusion, ProteinMPNN, ESMFold) and binding prediction (PRODIGY).

## Project Structure

```
├── data/
│   ├── input/              # Input PDB (6A0Z.pdb - HA:13D4 complex)
│   └── epitope/            # Epitope residues & hotspots (JSON + TXT)
├── stage1_generation/      # RFDiffusion backbones + ProteinMPNN sequences
│   ├── backbones/          # PDB files from RFDiffusion
│   └── filtered/           # Sequences passing MPNN score + CDR diversity
├── stage2_verification/    # ESMFold structure predictions + validation
│   ├── esmfold_outputs/    # PDB predictions
│   └── passed/             # Structures passing pLDDT ≥ 80 & RMSD < 2.0 Å
├── stage3_evaluation/      # PRODIGY binding prediction + ranking
│   ├── complexes/          # Ab-HA complex PDB files
│   └── top5_candidates/    # Final ranked candidates
├── results/                # Output JSON/CSV logs
├── scripts/                # Python utilities (local execution)
└── notebooks/              # Google Colab notebooks (GPU stage execution)
```

## Notion Integration

**Tracking Databases:**
- [H5N1 Project Progress](https://app.notion.com/p/db6185a3f9c84b36a4e9b59798266aa1) — Pipeline stage status
- [H5N1 Candidates](https://app.notion.com/p/9a7070e71cb142208e4a4f3c897b18cd) — Antibody candidates (pLDDT, ΔG, scores, ranks)

## Pipeline Stages

### Pre-Stage: Epitope Extraction (Local)
Extract interface residues from 6A0Z.pdb (HA:13D4 antibody complex) using:
- **Distance-based**: HA CA within 5.0 Å of antibody CA
- **BSA hotspots**: Buried surface area > 30.0 Ų (Shrake-Rupley SASA)

**Status**: ✅ Complete (2 epitopes, 1 hotspot: A:159)

**Outputs**:
- `data/epitope/epitope_residues.json` — Detailed residue metrics
- `data/epitope/hotspot_residues.txt` — Comma-separated hotspot IDs for RFDiffusion

**Run locally**:
```bash
python scripts/prestage_extract_epitope.py
```

### Stage 1: Generation & Filtering (Colab T4)
**1A. RFDiffusion**: Generate 30 backbones conditioned on epitope hotspots.
**1B. ProteinMPNN**: Sequence design + filtering (MPNN score, CDR diversity).

**Input**: `data/epitope/hotspot_residues.txt`
**Output**: 20 filtered sequences → `stage1_generation/filtered/*.fa`

### Stage 2: Structure Validation (Colab T4)
**ESMFold**: Fold all sequences from Stage 1.
**Filters**: pLDDT ≥ 80, RMSD < 2.0 Å vs. original backbone.

**Input**: `stage1_generation/filtered/*.fa`
**Output**: 10 validated structures → `stage2_verification/passed/*.pdb`

### Stage 3: Binding Evaluation (Colab/Local)
**PRODIGY**: Predict binding affinity (ΔG) for Ab:HA complexes.
**Ranking**: Composite score = 0.5×(pLDDT norm) + 0.5×(ΔG norm).

**Input**: `stage2_verification/stage2_validated.csv` + structure PDBs
**Output**: Top 5 candidates → `stage3_evaluation/top5_candidates/`

## Setup

### Local Environment
```bash
pip install biopython numpy pandas scipy
python scripts/prestage_extract_epitope.py
```

### Google Colab
1. Mount Google Drive
2. Clone this repo
3. Install GPU packages: `localcolabfold`, `torch`, `GitPython`, `notion-client`
4. Set environment variables: `GITHUB_TOKEN`, `NOTION_TOKEN`, `GITHUB_USER`
5. Run stage notebooks

## Environment Variables

See `.env.example` for required keys:
```bash
cp .env.example .env  # Edit with your credentials
```

- `GITHUB_TOKEN`: Personal access token (repo write access)
- `NOTION_TOKEN`: Notion API key
- `GITHUB_USER`: GitHub username (for repo URL)

## Outputs

- **CSV Summaries**: 
  - `stage2_verification/stage2_validated.csv`
  - `stage3_evaluation/composite_scores.csv`
- **JSON Logs**: `results/pipeline_log.json`
- **PDB Files**: `stage1_generation/`, `stage2_verification/passed/`, `stage3_evaluation/top5_candidates/`

## Citation

Based on:
- **RFDiffusion**: Watson et al., Nature (2023)
- **ProteinMPNN**: Dauparas et al., Nature (2022)
- **ESMFold**: Lin et al., bioRxiv (2022)
- **PRODIGY**: Vangone & Bonvin, PLoS Comput. Biol. (2015)

PDB: 6A0Z (Broadly neutralizing antibody 13D4 with H5N1 HA — Lingwood et al., PNAS 2012)

## License

MIT
