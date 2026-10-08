#!/usr/bin/env bash
# Publish a badge file to a branch of the origin remote.
#
# Usage: publish-badge.sh <badge-file> <target-branch> <path-in-branch> <commit-message>
#
# Builds the commit with git plumbing on a temporary index, so the caller's
# checkout and working tree are never touched. Creates the target branch as an
# orphan when it does not exist yet, skips the commit when the badge did not
# change and retries when a concurrent run pushed first.
#
# Prints "pushed" or "unchanged" to stdout.
set -euo pipefail

if [[ $# -ne 4 ]]; then
	echo "Usage: $0 <badge-file> <target-branch> <path-in-branch> <commit-message>" >&2
	exit 2
fi

badge_file=$1
branch=$2
target_path=$3
message=$4

export GIT_AUTHOR_NAME="github-actions[bot]"
export GIT_AUTHOR_EMAIL="41898282+github-actions[bot]@users.noreply.github.com"
export GIT_COMMITTER_NAME=$GIT_AUTHOR_NAME
export GIT_COMMITTER_EMAIL=$GIT_AUTHOR_EMAIL

tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT
export GIT_INDEX_FILE="$tmp_dir/index"

blob=$(git hash-object -w "$badge_file")

for attempt in 1 2 3; do
	rm -f "$GIT_INDEX_FILE"
	parent=""
	ls_remote_status=0
	git ls-remote --exit-code --heads origin "refs/heads/$branch" >/dev/null || ls_remote_status=$?
	if [[ $ls_remote_status -eq 0 ]]; then
		git fetch --quiet --no-tags origin "refs/heads/$branch"
		parent=$(git rev-parse FETCH_HEAD)
		git read-tree "$parent"
	elif [[ $ls_remote_status -ne 2 ]]; then
		echo "Could not reach the origin remote" >&2
		exit 1
	fi

	git update-index --add --cacheinfo "100644,$blob,$target_path"
	tree=$(git write-tree)
	if [[ -n $parent && $tree == "$(git rev-parse "$parent^{tree}")" ]]; then
		echo "unchanged"
		exit 0
	fi

	if [[ -n $parent ]]; then
		commit=$(git commit-tree "$tree" -p "$parent" -m "$message")
	else
		commit=$(git commit-tree "$tree" -m "$message")
	fi

	if git push --quiet origin "$commit:refs/heads/$branch"; then
		echo "pushed"
		exit 0
	fi
	echo "Push to $branch failed (attempt $attempt), retrying" >&2
	sleep $((attempt * 2))
done

echo "Could not push the badge to $branch. Check that the job has 'permissions: contents: write'" >&2
echo "and that no ruleset blocks github-actions[bot] from pushing to that branch." >&2
exit 1
