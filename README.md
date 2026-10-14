# Electives Atlas

The website is generated automatically from the PDFs in `electives/`.

## Initial setup

1. Create a **public** GitHub repository called `electives-atlas`, with the branch named `main`.
2. Upload all contents of this repository ZIP (not the ZIP itself) to the repository root, including the `.github` folder.
3. Under **Settings → Pages → Build and deployment**, set **Source: GitHub Actions**.
4. Under **Actions**, select **Build Electives Atlas and publish**, then **Run workflow** (branch `main`) if no automatic build started.
5. Visit `https://YOUR-USERNAME.github.io/electives-atlas/` after the workflow succeeds.

If `.github` was hidden and missed during browser upload, create the file `.github/workflows/publish.yml` manually using the text in `WORKFLOW-COPY.txt`.

## Future updates

Open the `electives` folder. Upload replacement or new group PDFs, or delete old ones, and **Commit changes**. GitHub Actions automatically regenerates the site. Keep exactly one PDF per course code/elective group combination. If you remove all groups belonging to a course, it disappears from the website. A PDF with invalid structure stops the build rather than silently publishing incomplete data; the previously published site stays available.

The PDFs must follow the Akari elective group export structure provided in the source archive. The generator reads the affiliated course name/code and the module stage/semester from the PDFs. This is build-time parsing, not client-side PDF parsing.

## Rules

- `CE2020`, `CE2021` and `CE2022` are excluded in all views and exports.
- The All Electives view merges repeated module codes **within the same stage and semester**.
- Separate elective groups remain separate in the course view.
- Groups that only contain excluded placement modules do not display.
- PDFs are inputs to the build only; they aren't copied into the published site.

## Local test

Run `pip install 'PyMuPDF>=1.24,<2'` and `python scripts/build.py`. Open `dist/index.html` in a browser.
