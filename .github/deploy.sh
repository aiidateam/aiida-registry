#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

SOURCE_BRANCH="master"
TARGET_BRANCH="gh-pages"

# Pull requests and commits to other branches shouldn't try to deploy, just build to verify
if [ "$GITHUB_ACTIONS" != "true" ]; then
    echo "Skipping deploy; just doing a build."
    exit 0
fi

# Save some useful information
REPO=$GITHUB_REPOSITORY
SSH_REPO=${REPO/https:\/\/github.com\//git@github.com:}
SHA=$GITHUB_SHA

mv out ../page-build
git checkout $TARGET_BRANCH || git checkout --orphan $TARGET_BRANCH
rm -rf * || exit 0
cp -r ../page-build/* .

git add -A .
# If there are no changes to the compiled out (e.g. this is a README update) then just bail.
if git diff --cached --quiet; then
    echo "No changes to the output on this push; exiting."
    exit 0
fi

git commit -m "Deploy to GitHub Pages: ${SHA}"

# Now that we're all set up, we can push.
git push

## Get the deploy key by using Travis's stored variables to decrypt deploy_key.enc
#ENCRYPTED_KEY_VAR="encrypted_${ENCRYPTION_LABEL}_key"
#ENCRYPTED_IV_VAR="encrypted_${ENCRYPTION_LABEL}_iv"
#ENCRYPTED_KEY=${!ENCRYPTED_KEY_VAR}
#ENCRYPTED_IV=${!ENCRYPTED_IV_VAR}
#openssl aes-256-cbc -K $ENCRYPTED_KEY -iv $ENCRYPTED_IV -in deploy_key.enc -out deploy_key -d
#chmod 600 deploy_key
#eval `ssh-agent -s`
#ssh-add deploy_key

# Clone the existing gh-pages for this repo into out/
# Create a new empty branch if gh-pages doesn't exist yet (should only happen on first deply)
#git clone $REPO out
#cd out
#git checkout $TARGET_BRANCH || git checkout --orphan $TARGET_BRANCH
#cd ..

# Clean out existing contents
#rm -rf out/* || exit 0
#

## Now let's go have some fun with the cloned repo
#cd out
#git config user.name "Travis CI"
#git config user.email "$COMMIT_AUTHOR_EMAIL"

# copy built HTML pages from top-level directory
#cp -r ../../out/* .

#git add -A .
# If there are no changes to the compiled out (e.g. this is a README update) then just bail.
#if git diff --cached --quiet; then
#    echo "No changes to the output on this push; exiting."
#    exit 0
#fi

# Commit the "changes", i.e. the new version.
# The delta will show diffs between new and old versions.
git commit -m "Deploy to GitHub Pages: ${SHA}"

# Now that we're all set up, we can push.
git push $SSH_REPO $TARGET_BRANCH
