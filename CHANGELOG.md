# Changelog

## 2026-08-04

### Fixes
- **[etl_vacancies]** Fix source file path derivation to use the run date and make vacancy transform resilient to invalid `published_at` values (#71)

### Chores
- **[etl_vacancies]** Add CLAUDE.md project guidelines, test coverage for vacancy transform and source filename date formatting, and document date-based source file naming (#71, #72)

## 2026-07-21

### Features
- **[rag]** Add a Retrieval-Augmented Generation pipeline (document embedding, indexing, and querying) (#63)
- **[image_upload_api]** Add async image processing via a Celery task queue (#60)

### Fixes
- **[.github]** Fix CI workflows to run pytest from the correct project folder (#65)

### Chores
- **[flask]** Add CLAUDE.md project documentation (#69)
- **[image_upload_api]** Add CLAUDE.md project documentation (#69)
- **[root]** Remove duplicated description from the root README (#68)
- **[image_upload_api]** Simplify README by removing a duplicated flow description (#67)
- **[.github]** Enable manual (workflow_dispatch) triggers for the coffee_machine and number_guessing CI workflows (#66)
- **[root]** Rewrite the root README as a portfolio index describing all projects (#64)
- **[learning]** Consolidate learning exercises and course work under fun_projects/learning/ (#64)
- **[.github]** Update CI workflow paths for the learning-projects relocation (#64)
- **[image_upload_api]** Document the async upload flow, task status endpoint, and scoped images in the README (#61)
