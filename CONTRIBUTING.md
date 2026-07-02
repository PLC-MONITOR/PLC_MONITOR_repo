# Contributing to this project

Thanks for helping out! This project runs on **trust and autonomy** — anyone with
Write access can push changes directly, no approval needed from anyone. There are
only two hard rules, enforced by GitHub itself:

## 🚫 The two things nobody can do (enforced, not just requested)

1. **No force-pushing to `main`** — history can't be rewritten or overwritten
2. **No deleting `main`** — it always has to exist

Everything else is fair game. You don't need my permission, a review, or a PR
approval to ship changes.

## ✅ How to work

You're free to work however suits you. Two common patterns:

**Direct and fast:**
```bash
git clone <repo-url>
# make your changes
git add .
git commit -m "what you did"
git push origin main
```

**Your own version/branch** (if you want to try something bigger without affecting
what others are doing):
```bash
git checkout -b v2-your-idea
git push origin v2-your-idea
```
You can merge it into `main` yourself whenever you're ready — no one needs to
approve it.

## 🏷️ Version tags

The original uploaded version is permanently tagged as `v1.0` and also published under
**Releases**. Even if `main` evolves over time, you can always download or check out the
exact original code:

```bash
git checkout v1.0
```

Please tag major milestones the same way (`v2.0`, `v2.1`, etc.) so we always have
restore points.

## 🙋 Working together

No coordination is required, but if you're about to make a big change and want to
avoid stepping on someone else's work, an Issue or a quick message to the group is
an easy way to give a heads-up. Totally optional.

Thanks for contributing! 🎉
