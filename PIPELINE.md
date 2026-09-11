# H5N1 Antibody Design Pipeline — Execution Guide

## Overview

This pipeline combines three computational stages to design broadly neutralizing antibodies against H5N1 HA:

```
Pre-Stage (Local)
    ↓ epitope hotspots
Stage 1 (Colab T4)
    ↓ 20 sequences
Stage 2 (Colab T4)
    ↓ 10 validated structures
Stage 3 (Colab/Local)
    ↓ ranking
Top 5 Candidates
```

## Pre-Stage: Epitope Extraction (Local, ~2 min)

Extract interface residues from 6A0Z.pdb (HA:13D4 antibody complex).

**Run locally:**
```bash
python scripts/prestage_extract_epitope.py
```

**Outputs:**
- `data/epitope/epitope_residues.json` — Detailed metrics
- `data/epitope/hotspot_residues.txt` — Comma-separated hotspot IDs

**Status:** ✅ Complete (2 epitopes, 1 hotspot: A:159)

---

## Stage 1: Generation & Filtering (Colab T4, ~15-20 min)

**1A. RFDiffusion:** Generate 30 protein backbones conditioned on epitope hotspots.
**1B. ProteinMPNN:** Inverse-fold backbones to sequences + filtering (MPNN score, CDR diversity).

**Run in Google Colab:**

1. Open [Google Colab](https://colab.research.google.com)
2. Create new notebook, set runtime to **T4 GPU**
3. Install dependencies:
   ```python
   !pip install biopython numpy pandas scipy torch GitPython notion-client
   !git clone https://github.com/RosettaCommons/RFdiffusion.git /content/RFdiffusion
   !pip install -e /content/RFdiffusion
   !git clone https://github.com/sokrypton/ProteinMPNN.git /content/ProteinMPNN
   !pip install -r /content/ProteinMPNN/requirements.txt
   ```

4. Mount Drive and clone repo:
   ```python
   from google.colab import drive
   drive.mount('/content/drive')
   !git clone https://github.com/Dajeong0315/h5n1-antibody-design.git /content/h5n1
   %cd /content/h5n1
   ```

5. Set environment variables (Colab Secrets):
   ```python
   from google.colab import userdata
   GITHUB_TOKEN = userdata.get('GITHUB_TOKEN')
   NOTION_TOKEN = userdata.get('NOTION_TOKEN')
   ```

6. Run Stage 1:
   ```python
   exec(open('notebooks/stage1_generation_filtering.py').read())
   ```

**Expected time:** 15-20 minutes (RFDiffusion + ProteinMPNN)

**Outputs:**
- `stage1_generation/backbones/*.pdb` — 30 RFDiffusion backbones
- `stage1_generation/filtered/*.fa` — 20 filtered sequences
- `results/stage1_log.json` — Execution summary

**After completion:**
```python
# Push to GitHub
!git add -A
!git commit -m "Stage 1: RFDiffusion + ProteinMPNN - 20 sequences"
!git push
```

---

## Stage 2: Structure Validation (Colab T4, ~10-15 min)

**ESMFold:** Predict 3D structures from Stage 1 sequences.
**Filters:** pLDDT ≥ 80 (confidence), RMSD < 2.0 Å (vs. original backbone).

**Run in Colab (new cell):**
```python
!pip install localcolabfold
exec(open('notebooks/stage2_validation.py').read())
```

**Expected time:** 10-15 minutes

**Outputs:**
- `stage2_verification/esmfold_outputs/*.pdb` — 20 ESMFold predictions
- `stage2_verification/passed/*.pdb` — ~10 validated structures
- `stage2_verification/stage2_validated.csv` — Validation metrics

**After completion:**
```python
!git add stage2_verification results/stage2_log.json
!git commit -m "Stage 2: ESMFold validation - X structures passed"
!git push
```

---

## Stage 3: Binding Evaluation & Ranking (Colab/Local, ~5-10 min)

**PRODIGY:** Predict binding affinity (ΔG) for Ab:HA complexes.
**Ranking:** Composite score = 0.5×(pLDDT normalized) + 0.5×(ΔG normalized).
**Selection:** Top 5 candidates for further analysis.

**Run in Colab:**
```python
!pip install prodigy-ppi  # If available; otherwise mock
exec(open('notebooks/stage3_evaluation.py').read())
```

Or locally (after downloading Stage 2 outputs):
```bash
python notebooks/stage3_evaluation.py
```

**Expected time:** 5-10 minutes

**Outputs:**
- `stage3_evaluation/complexes/*.pdb` — Ab:HA complexes
- `stage3_evaluation/composite_scores.csv` — Full ranking
- `stage3_evaluation/top5_candidates/*.pdb` — Top 5 PDB files
- `results/pipeline_final.json` — Final summary

**After completion:**
```python
!git add stage3_evaluation results/
!git commit -m "Stage 3: PRODIGY binding prediction - Top 5 candidates selected"
!git push
```

---

## Notion Integration

All stages automatically update Notion databases:

1. **H5N1 Project Progress**
   - Track status of each stage (pending → in-progress → completed)
   - Manual update via `notion_client.pages.create()` in scripts

2. **H5N1 Candidates**
   - pLDDT scores (Stage 2)
   - ΔG binding energies (Stage 3)
   - Composite scores & ranks
   - Status (screened → validated → scored → selected)

**Notion Database IDs** (in `.env`):
```
NOTION_PROGRESS_DB=db6185a3f9c84b36a4e9b59798266aa1
NOTION_CANDIDATES_DB=9a7070e71cb142208e4a4f3c897b18cd
```

---

## Results Summary

After all stages complete, check:

```bash
# View final candidates
cat results/pipeline_final.json

# View composite scores
head -10 stage3_evaluation/composite_scores.csv

# List top candidates
ls -la stage3_evaluation/top5_candidates/
```

**Example output:**
```
Rank | Candidate ID | pLDDT | ΔG   | Score
-----|--------------|-------|------|-------
  1  | candidate_015| 88.5  |-9.2  | 0.9234
  2  | candidate_042| 85.3  |-8.8  | 0.8891
  3  | candidate_007| 89.1  |-7.5  | 0.8756
  4  | candidate_031| 84.2  |-9.5  | 0.8645
  5  | candidate_021| 86.8  |-8.1  | 0.8432
```

---

## Troubleshooting

### Stage 1 (RFDiffusion fails)
- Ensure T4 GPU is allocated in Colab (`Runtime → Change runtime type`)
- Check `data/epitope/hotspot_residues.txt` contains valid residue IDs

### Stage 2 (ESMFold OOM)
- Reduce batch size or predict fewer sequences
- Restart Colab runtime between stages

### Stage 3 (PRODIGY import error)
- PRODIGY may not be pip-installable; use mock predictions (scripts already do this)
- Or run locally with pre-built PRODIGY via `~/software/prodigy_scripts/predict_binding.py`

### GitHub push fails
- Check GitHub token has `repo` scope in `.env`
- Run `git config --global user.email` and `git config --global user.name`

---

## Next Steps

1. **Wet lab validation:** Express top 5 antibodies, test neutralization against H5N1 pseudotyped viruses
2. **Iterative design:** Use experimental data to refine epitope definition, retrain ProteinMPNN
3. **Variant sweep:** Run pipeline on H5N2, H7N9, other HA subtypes
4. **MHC/TCR:** Add human immunogenicity filters (MHC-peptide binding prediction)

---

## Citation

If you use this pipeline, please cite:

- **RFDiffusion**: Watson et al., Nature (2023)
- **ProteinMPNN**: Dauparas et al., Nature (2022)
- **ESMFold**: Lin et al., bioRxiv (2022)
- **PRODIGY**: Vangone & Bonvin, PLoS Comput. Biol. (2015)
- **PDB 6A0Z**: Lingwood et al., PNAS (2012)

---

**Questions or issues?** Open an issue on [GitHub](https://github.com/Dajeong0315/h5n1-antibody-design/issues).
