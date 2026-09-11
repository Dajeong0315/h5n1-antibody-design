# H5N1 Antibody Design Pipeline — Quick Start

## ✅ What's Ready

Your H5N1 antibody design pipeline is **fully set up** and ready to run. Here's what's been completed:

### Local Environment (Windows)
- ✅ Project folder structure created
- ✅ Git repository initialized
- ✅ Pre-Stage script implemented: `scripts/prestage_extract_epitope.py`
- ✅ Pre-Stage executed: **2 epitopes, 1 hotspot (A:159) extracted**

### Cloud/Colab Infrastructure
- ✅ Stage 1 code ready: `notebooks/stage1_generation_filtering.py` (RFDiffusion + ProteinMPNN)
- ✅ Stage 2 code ready: `notebooks/stage2_validation.py` (ESMFold + validation)
- ✅ Stage 3 code ready: `notebooks/stage3_evaluation.py` (PRODIGY + ranking)
- ✅ Execution guide: `PIPELINE.md` (step-by-step instructions)

### Notion Integration
- ✅ Database 1: **H5N1 Project Progress** — Stage tracking
  - Pre-Stage marked **complete** (2 epitopes, 1 hotspot)
  - Stages 1-3 set to **pending**
- ✅ Database 2: **H5N1 Candidates** — Antibody tracking
  - Ready to record pLDDT (Stage 2), ΔG (Stage 3), scores & ranks

### GitHub Repository
- ✅ Remote linked: https://github.com/Dajeong0315/h5n1-antibody-design
- ✅ 2 commits pushed with full documentation
- ✅ `.env.example` ready (fill with your credentials)

---

## 🚀 Next Steps (Run the Pipeline)

### **Option 1: Full Pipeline on Google Colab (Recommended)**

**Time estimate:** ~40-50 minutes (15+15+10 min for GPU stages)

1. **Prepare credentials** (one-time setup):
   - GitHub: Create Personal Access Token at https://github.com/settings/tokens (check `repo` scope)
   - Notion: Create API key at https://www.notion.so/my-integrations
   - Copy `.env.example` → `.env` locally, fill in credentials

2. **Open Google Colab:**
   - Go to https://colab.research.google.com
   - Create new notebook, **set Runtime → Change runtime type → GPU (T4)**

3. **Run in Colab cells:**

   ```python
   # Mount Drive & clone repo
   from google.colab import drive, userdata
   drive.mount('/content/drive')
   !git clone https://github.com/Dajeong0315/h5n1-antibody-design.git /content/h5n1
   %cd /content/h5n1
   
   # Set credentials
   GITHUB_TOKEN = userdata.get('GITHUB_TOKEN')
   NOTION_TOKEN = userdata.get('NOTION_TOKEN')
   GITHUB_USER = userdata.get('GITHUB_USER')
   ```

   ```python
   # Stage 1: RFDiffusion + ProteinMPNN (15 min)
   !pip install biopython numpy pandas scipy torch GitPython notion-client
   # Install RFDiffusion & ProteinMPNN (see PIPELINE.md for full commands)
   exec(open('notebooks/stage1_generation_filtering.py').read())
   ```

   ```python
   # Stage 2: ESMFold (15 min)
   !pip install localcolabfold
   exec(open('notebooks/stage2_validation.py').read())
   ```

   ```python
   # Stage 3: PRODIGY + Ranking (10 min)
   exec(open('notebooks/stage3_evaluation.py').read())
   
   # View results
   import json
   with open('results/pipeline_final.json') as f:
       print(json.dumps(json.load(f), indent=2))
   ```

4. **After completion:**
   ```python
   !git add -A
   !git commit -m "Pipeline complete: Top 5 candidates selected"
   !git push
   ```

### **Option 2: Local Execution (Pre-Stage Only)**

If you just want to test Pre-Stage locally:

```bash
cd C:\Users\aicam\Projects\h5n1-antibody-design
python scripts/prestage_extract_epitope.py
```

Results already in: `data/epitope/` ✅

---

## 📊 Expected Results

After full pipeline (Stages 1-3):

### **CSV Output** (`stage3_evaluation/composite_scores.csv`)
```
candidate_id,plddt,delta_g,composite_score,rank
candidate_015,88.5,-9.2,0.9234,1
candidate_042,85.3,-8.8,0.8891,2
candidate_007,89.1,-7.5,0.8756,3
...
```

### **Notion Candidates DB** (Auto-populated)
- Each candidate row with: pLDDT, ΔG, Composite Score, Rank, Status → "selected" for Top 5

### **GitHub** (`results/pipeline_final.json`)
```json
{
  "project": "H5N1_Ab_Design",
  "summary": {
    "pre_stage": {"epitopes": 2, "hotspots": 1},
    "stage1": {"backbones": 30, "sequences_filtered": 20},
    "stage2": {"validated_structures": 10},
    "stage3": {"final_candidates": 5}
  },
  "top_5": [
    {"candidate_id": "candidate_015", "rank": 1, "plddt": 88.5, "delta_g": -9.2, ...},
    ...
  ]
}
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "GitHub push fails" | Check `.env` has valid `GITHUB_TOKEN` with `repo` scope |
| "RFDiffusion not found" | Install via `pip install -e /content/RFdiffusion` in Colab |
| "ESMFold runs out of memory" | Reduce batch size or skip-run with mock predictions (already in code) |
| "Notion database not found" | Verify `NOTION_TOKEN` is valid and database IDs in `.env` match |
| "6A0Z.pdb not found" | File should already be in `data/input/6A0Z.pdb` (downloaded in setup) |

---

## 📚 Documentation

- **`README.md`** — Project overview & structure
- **`PIPELINE.md`** — Detailed execution guide (all stages)
- **`requirements.txt`** — Python dependencies
- **`.env.example`** — Credentials template (copy → `.env` and fill)

---

## 📁 Repo Structure

```
h5n1-antibody-design/
├── README.md                          # Project overview
├── PIPELINE.md                        # Execution guide
├── QUICKSTART.md                      # This file
├── requirements.txt                   # Dependencies
├── .env.example                       # Credentials template
├── data/
│   ├── input/6A0Z.pdb                # HA:13D4 complex (input)
│   └── epitope/                       # Pre-Stage outputs (JSON + hotspots)
├── scripts/
│   └── prestage_extract_epitope.py   # Pre-Stage script (local)
├── notebooks/
│   ├── stage1_generation_filtering.py # Stage 1 (RFDiffusion + MPNN)
│   ├── stage2_validation.py           # Stage 2 (ESMFold)
│   └── stage3_evaluation.py           # Stage 3 (PRODIGY + ranking)
├── results/
│   ├── stage1_log.json               # Stage 1 summary
│   ├── stage2_log.json               # Stage 2 summary
│   ├── stage3_log.json               # Stage 3 summary
│   └── pipeline_final.json           # Final results
└── stage*_*/                          # Output directories (created during run)
    ├── backbones/                     # RFDiffusion outputs
    ├── filtered/                      # MPNN sequences
    ├── esmfold_outputs/               # ESMFold predictions
    ├── passed/                        # Validated structures
    ├── complexes/                     # Ab:HA complexes
    └── top5_candidates/               # Final candidates
```

---

## 🎯 Key Features

✅ **Automated epitope extraction** (Shrake-Rupley SASA)  
✅ **GPU-accelerated design** (RFDiffusion, ProteinMPNN, ESMFold)  
✅ **Multi-filter validation** (pLDDT, RMSD, diversity)  
✅ **Binding prediction** (PRODIGY ΔG)  
✅ **Composite scoring** (pLDDT + ΔG normalized)  
✅ **Notion tracking** (real-time progress updates)  
✅ **GitHub versioning** (full reproducibility)  

---

## 💡 Tips

1. **First run:** Use mock predictions (already enabled in Stage 1-3 code) to test pipeline logic without GPU time
2. **Production run:** Comment out mock prediction lines and use actual RFDiffusion/ESMFold
3. **Incremental:** Run stages independently; outputs are persisted to disk
4. **Monitor:** Check Notion databases for live progress updates

---

## ❓ Need Help?

- See `PIPELINE.md` for step-by-step instructions
- Check GitHub Issues: https://github.com/Dajeong0315/h5n1-antibody-design/issues
- Review logs: `results/stage*_log.json`

---

## 🎉 You're Ready!

**Everything is set up.** Your next step is to open Google Colab and run Stages 1-3. 

Good luck with your H5N1 antibody design! 🧬

---

*Last updated: 2026-09-11*
