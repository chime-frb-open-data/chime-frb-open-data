# Contribute to the CHIME/FRB Open Data Project

Want to hack on the CHIME/FRB Open Data? Want to contribute towards a community of robust tools to analyze radio transients? You are at the right place!

## Topics

* Report an Issue
* Open a Pull Request

## Report an Issue
A great way to contribute to the project is to send a detailed report when you
encounter an issue. We always appreciate a well-written, thorough bug report,
and will thank you for it!

Check that [our issue database](https://github.com/chime-frb-open-data/chime-frb-open-data/issues)
doesn't already include that problem or suggestion before submitting an issue.
If you find a match, you can use the "subscribe" button to get notified on
updates. Do *not* leave random "+1" or "I have this too" comments, as they
only clutter the discussion, and don't help resolving it. However, if you
have ways to reproduce the issue or have additional information that may help
resolving the issue, please leave a comment.

When reporting issues, always insure,
  - Version of `cfod` installed.

Also include the steps required to reproduce the problem if possible and
applicable. This information will help us review and fix your issue faster.
When sending lengthy log-files, consider posting them as a [gist](https://gist.github.com).
Don't forget to remove sensitive data from your logfiles before posting (you can
replace those parts with "REDACTED").

## Open a Pull Request
Not sure if that typo is worth a pull request? Found a bug and know how to fix
it? Do it! We will appreciate it. Any significant improvement should be
documented as [a GitHub issue](https://github.com/chime-frb-open-data/chime-frb-open-data/issues) before
anybody starts working on it.

We are always thrilled to receive pull requests. We do our best to process them
quickly!

### Accepted Proposals
You can propose new designs for existing `cfod` features. You can also design
entirely new features. We really appreciate contributors who want to refactor or
otherwise cleanup our project.

### Conventions

Fork the repository and make changes on your fork in a feature branch:

- If it's a bug fix branch, name it XXXX-something where XXXX is the number of
	the issue. 
- If it's a feature branch, create an enhancement issue to announce
	your intentions, and name it XXXX-something where XXXX is the number of the
	issue.

Update the [documentation](https://github.com/chime-frb-open-data/chime-frb-open-data.github.io) when creating or modifying features. Test your
documentation changes for clarity, concision, and correctness, as well as a clean documentation build.

Write clean code. Universally formatted code promotes ease of writing, reading,
and maintenance. Always run `black .` on each changed file before
committing your changes. Most editors have plug-ins that do this automatically.

Pull request descriptions should be as clear as possible and include a reference
to all the issues that they address.

### Review

Code review comments may be added to your pull request. Discuss, then make the
suggested modifications and push additional commits to your feature branch. Post
a comment after pushing. New commits show up in the pull request automatically,
but the reviewers are notified only when you comment.

Pull requests must be cleanly rebased on top of master without multiple branches
mixed into the PR.

**Git tip**: If your PR no longer merges cleanly, use `rebase master` in your
feature branch to update your pull request rather than `merge master`.

Before you make a pull request, squash your commits into logical units of work
using `git rebase -i` and `git push -f`. A logical unit of work is a consistent
set of patches that should be reviewed together: for example, upgrading the
version of a vendored dependency and taking advantage of its now available new
feature constitute two separate units of work. Implementing a new function and
calling it in another file constitute a single logical unit of work. The very
high majority of submissions should have a single commit, so if in doubt: squash
down to one.

After every commit, [make sure the test suite passes (WIP)](). Include
documentation changes in the same pull request so that a revert would remove
all traces of the feature or fix.

Include an issue reference like `Closes #XXXX` or `Fixes #XXXX` in commits that
close an issue. Including references automatically closes the issue on a merge.






