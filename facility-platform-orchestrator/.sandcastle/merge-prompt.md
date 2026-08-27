# TASK

Merge the following branches into the current branch:

{{BRANCHES}}

For each branch:

1. Run `git merge <branch> --no-edit`
2. If there are merge conflicts:
   - Read both sides carefully
   - For additive changes (new exports, new screen files, new store files): keep both
   - For `src/navigation/types.ts`: keep all type declarations from both sides
   - For any navigator file: each branch owns a different navigator — keep all
   - After resolving, run `git add -A` then `git merge --continue`
3. After each successful merge, run `npx tsc --noEmit` to verify TypeScript is still clean
4. If TypeScript errors appear after merging a branch, fix them before proceeding to the next branch

After all branches are merged, make a single summary commit.

# CLOSE ISSUES

Issues merged in this round:

{{ISSUES}}

Close each issue using these commands:

{{CLOSE_COMMANDS}}

Once everything is merged and issues are closed, output `<promise>COMPLETE</promise>`.
