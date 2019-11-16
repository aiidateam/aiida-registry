#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

# commit sha of master branch
SHA=`git rev-parse --verify HEAD`
TARGET_BRANCH="gh-pages"

if [ "$GITHUB_ACTIONS" != "true" ]; then
    echo "Skipping deploy; just doing a build."
    exit 0
fi

# move html to temp dir
mv out ../page-build
git checkout $TARGET_BRANCH || git checkout --orphan $TARGET_BRANCH
rm -rf * || exit 0
cp -r ../page-build/* .

git config user.name "$COMMIT_AUTHOR"
git config user.email "$COMMIT_AUTHOR_EMAIL"

git add -A .
# If there are no changes to the compiled out (e.g. this is a README update) then just bail.
if git diff --cached --quiet; then
    echo "No changes to the output on this push; exiting."
    exit 0
fi

git commit -m "Deploy to GitHub Pages: ${SHA}"
