# Git and GitHub Workflow

## Current Remote

- GitHub repository: https://github.com/Cronosfather/project_MARS
- Local branch: `master`
- Upstream branch: `origin/master`
- First pushed commit after workflow setup: `cbfa817`

## Policy

This project should use frequent local commits and regular GitHub pushes.

Recommended rhythm:

1. Commit whenever code, configuration, or documentation reaches a meaningful checkpoint.
2. Push at the end of each work block, before long CFD runs, and after important results are summarized.
3. Do not commit raw heavy CFD outputs unless there is a specific reason.
4. Commit scripts, templates, case definitions, summary CSV files, and research notes.

## What Should Be Tracked

Track:

- Python scripts under `scripts/`
- Configuration files under `config/`
- Gmsh templates under `geometry/gmsh_templates/`
- Airfoil source coordinate files if they define the study setup
- Documentation under `docs/` and `research/`
- Small summary files that explain completed calculations
- Empty case directory placeholders such as `.gitkeep`

Do not track by default:

- SU2 restart files
- Large mesh files
- Large solver logs
- Raw VTK/volume/surface output
- Generated case directories with full solver output
- Temporary cache files

The `.gitignore` file is configured so generated case contents are ignored while `.gitkeep` files keep the important directory structure visible.

## Practical Commands

Check status:

```powershell
git status -sb
```

Commit a completed work block:

```powershell
git add <files>
git commit -m "Short clear message"
```

Push to GitHub:

```powershell
git push
```

If a new branch is created:

```powershell
git push -u origin <branch-name>
```

## CFD-Specific Rule

Before a long run, push the setup first. This preserves the exact scripts, templates, and case definitions used to generate the calculation.

After a long run, do not push raw output immediately. First summarize the result into a small document or CSV, then commit and push that summary.

For the current 10000-iteration RANS stage, the preferred sequence is:

1. Keep the long-run setup committed and pushed.
2. Run the candidate case locally.
3. Postprocess the result.
4. Commit only the summary, updated status notes, and any script/config fixes.
5. Push the summary commit to GitHub.
