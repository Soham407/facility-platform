# ISSUES

Here are the open issues in the Solvesxx_mobile repo:

<issues-json>

!`gh issue list --state open --label ready-for-agent --repo Soham407/Solvesxx_mobile --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`

</issues-json>

# TASK

Analyze the open issues and build a dependency graph. For each issue, determine whether it **blocks** or **is blocked by** any other open issue.

An issue B is **blocked by** issue A if:
- B's body mentions "Blocked by #A" or "depends on #A"
- B requires code that A introduces (e.g., pre-stub navigators, type declarations)
- B and A modify the same file (merge conflict risk)

An issue is **unblocked** if it has zero blocking dependencies on other open issues.

For each unblocked issue, assign a branch name: `sandcastle/issue-{id}-{slug}`.

# OUTPUT

Output your plan as a JSON object wrapped in `<plan>` tags:

<plan>
{"issues": [{"id": "42", "title": "Pre-stub roles in RoleNavigator", "branch": "sandcastle/issue-42-pre-stub-roles"}]}
</plan>

Include **only unblocked issues**. If every issue is blocked, include the single highest-priority unblocked candidate (fewest/weakest dependencies).
