# Definition of Done

A story is considered "done" only when ALL of the following is true:

## Working and Verified
- Acceptance criteria manually checked 
- At least one failure case handled
- No Crashes - errors return meaninful responses

## Code Quality and Baseline
- Naming and formatting follows class standard (no klint or detekt errors)
- Route is thin (business logic not embedded in routing)
- No unsafe !! without justification
- No obvious duplicated logic

## Testing
- At least one of the following:
    1. One automated test (in github action)
    2. A written manual test checklist that was run.

## Pull Request and Integration
- Opened as PR (**not** directly pushed to main)
- At least one teammate reviewed it
- Reviewer confirmed:
    - Code is understandable
    - It meets the DoD
    - It doesn't break the existing functionality
    - Passes all github actions tests
- PR builds and runs after merge
