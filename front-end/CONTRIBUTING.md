# Contributing Guide

How to set up, code, test, review, and release so contributions meet our Definition of Done.

## Code of Conduct

All contributors are expected to follow the following standards of behavior:

* Respect: Communicate respectfully and constructively in all discussions and reviews.  
* Integrity: Provide efficient code, give proper attribution, and never commit code that violates privacy rules.  
* Reporting Issues: If any behavior violates these standards, please contact the repo owner. 

## Getting Started

List prerequisites, setup steps, environment variables/secrets handling, and how to run the app locally.  
No prerequisites.

1. Clone the repo from github: ​​[https://github.com/bradfiep/CS.067-Self-Organizing-AI-Agents-at-the-Edge](https://github.com/bradfiep/CS.067-Self-Organizing-AI-Agents-at-the-Edge)   
2. In frontend/ folder run npm install  
3. In the same folder run npm run  
4. Navigate to the localhost link displayed in the terminal

## Branching & Workflow

Describe the workflow (e.g., trunk-based or GitFlow), default branch, branch naming, and when to rebase vs. merge.  
1.The main application is kept on the main branch.   
2.The new branch is created with the name of the task from the GitHub Project with the main as parent branch: feature/bugfix \- ticket/task number in github \- specified small task. For example: feat-10-footer, for the ticket number 10 about visualizing UI components.  
3.All the work for the specific task should be done in that branch, then committed.  
4\. When the person is sure they are done with the work, a pull request has to be created for merging their branch with the main.  
5.Teammates review the pull request to approve/decline the merge. 2 votes are enough to merge/decline the pull request.

## Issues & Planning

Explain how to file issues, required templates/labels, estimation, and triage/assignment practices.

- File issues using the provided GitHub templates  
- Apply appropriate labels: bug, enhancement, documentation, etc.  
  - Each issue should include:  
    - Clear description  
    - Expected vs. actual behavior  
    - Steps to reproduce (if applicable)  
- Issues are triaged weekly. Estimation uses story points (1–8 scale).

## Commit Messages

State the convention (e.g., Conventional Commits), include examples, and how to reference issues.

Structure changes by stating the file name, function name, and reasoning (not necessarily in that order). 

Commit often to keep messages short (preferably below 50 chars)  and state changes clearly so we can have a good record of our progress. 

**Example:**

git commit \-m “added input sanitation to function user\_input() inside file helper\_funcs.py”

If the commit message requires a longer and more detailed description, give it a summary and leave the details in the body. 

**Example:**

git commit \-m “added input sanitation to function user\_input() inside file helper\_funcs.py” \-m “This was done by blah blah blah blah blah blah blah blah blah. Blah blah blah blah blah blah blah.”

You can also do this by using a text editor or by adding newlines within your commit message.

We will reference issues by assigning each issue it’s own branch and starting it with the type of issue and the  issue number.

**Example:**  
	“Feat-10-header-component” indicates that it is a feature and part of issue \#10 within our GitHub Project. 

## Code Style, Linting & Formatting

Name the formatter/linter, config file locations, and the exact commands to check/fix locally.

## Testing

Define required test types, how to run tests, expected coverage thresholds, and when new/updated tests are mandatory.

All new or modified code should include appropriate tests to ensure reliability and maintainability

**Types:** Unit, integration, and end-to-end (as applicable)  
**Frameworks:** Jest, Cypress  
**Run locally:** `npm test`  
**Coverage:** ≥ 60% overall test coverage  
      Focus on testing critical features and new logic rather than achieving full coverage

## Pull Requests & Reviews

Outline PR requirements (template, checklist, size limits), reviewer expectations, approval rules, and required status checks.

* 1 PR per feature or bug fix.  
  * Keep each PR focused on a single logical change.  
* PR size limits:  
  * If a feature adds too many lines of code or touches multiple modules, split it into smaller PRs.  
  * Each PR should be easy to review in one sitting (aim for \< 500 lines of diff where possible).  
* Template usage:  
  * Follow the standard PR template that includes:  
    * Summary of changes  
    * Related issue or ticket number  
    * Testing steps / screenshots (if applicable)  
    * Checklist for readiness (tests added, documentation updated, etc.)  
* Reviewer Expectations  
  * Review for code quality, clarity, and maintainability.  
  * Check that:  
    * Functions are small, direct, and do one thing well.  
    * Code is readable, consistent, and reuses existing functions where possible.  
    * There’s no unnecessary complexity—avoid over-engineering.  
    * Naming is clear and meaningful.  
    * Comments and documentation are present where logic isn’t self-explanatory.  
  * Provide constructive, specific feedback — avoid vague comments.  
* Approval Rules  
  * At least one approval from a designated reviewer or team lead required before merge.  
  * No self-approval for your own PRs

## CI/CD

* Pipeline Definitions:  
  * All CI/CD pipelines are defined in the repository under `.github/workflows/` (for GitHub Actions) or in the project’s CI directory.  
  * Each pipeline handles build, test, and deployment stages for consistent automation across environments.  
* Mandatory Jobs:  
  * Build: Must successfully compile without errors.  
  * Unit Tests: All tests must pass with acceptable coverage.  
  * Integration Tests (if applicable): Run automatically for major features or releases.  
    Security Scan: Detects vulnerabilities in dependencies.  
* Viewing Logs & Re-running Jobs:  
  * CI/CD job logs can be viewed directly in the repository’s Actions (or CI) tab.  
  * To re-run a failed job, click “Re-run all jobs” or “Re-run failed jobs” on the workflow page (requires proper permissions).  
* Requirements Before Merge / Release:  
  * All mandatory CI jobs must pass successfully.  
  * The branch must be up-to-date with main to prevent integration issues.  
  * All status checks (build, test, security) must show green.  
  * At least one approved code review must be completed.

## Security & Secrets

Reporting Vulnerabilities: Contact Repo owner if any vulnerabilities are seen.  
Prohibited: Never commit API keys, tokens, or credentials. Store in GitHub secrets.  
Dependency: Checked each sprint via `npm audit fix.`

## Documentation Expectations

Update documentation for any code, API, or config changes

- README.md  
- frontend/ README.md

Write clear comments and short descriptions in your code to explain how complex parts work.

## Release Process

Following the finalization on the simple ruleset for individual nodes to follow in receiving bias from peers and weighing against their own findings, we will begin to roll out versions.

**Versioning:** 

* PATCH (x.x.1): for backward compatible bug fixes  
* MINOR (x.1.x): for new, backwards compatible features  
* MAJOR (1.x.x): For breaking changes.

**Tagging:**  
When a Pull request is merged to the main branch at a scale that prompts a new or updated release, the person who completed the PR will be responsible for creating a new git tag for the version (e.g., v1.0.1). 

**Changelog:**   
A changelog will be manually created or updated in ChangeLog.md based on the merged Pull Requests since the last version.

**Deployment:**  
The CI/CD pipeline will automatically build and deploy the tagged version.

**Rollback:**   
In the event of a real issue, we can rollback by re-deploying a previous git tag.

## Support & Contact

**Contact Channel: [https://discord.gg/a6CdXFvq2P](https://discord.gg/a6CdXFvq2P)**   
**Expected response time:** Within 48 hours  
Questions can be asked in *\#questions* channel, using the invite link above.

