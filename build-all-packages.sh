#!/usr/bin/env bash
REPO="NixOS/nixpkgs"

curl -s "https://api.github.com/repos/$REPO/commits?per_page=1" \
  | jq '.[0] | {rev: .sha, name: .commit.message, date: .commit.author.date}' > last-commit.json

REV=$(jq --raw-output .rev last-commit.json)
echo "Using nixpkgs rev=$REV"

NIXPKGS_PATH=$(nix eval --impure --expr "
  let url = "https://github.com/NixOS/nixpkgs/archive/${REV}.tar.gz";
  in (fetchTarball { inherit url; })" | tr -d '"')

nix eval --impure  --json --expr "
  (import ./collect-packages.nix) { pkgs = import $NIXPKGS_PATH {}; }
" -vv > packages.json

cat packages.json | tr -d '["]' | tr ',' '\n' > packages

echo "starting build of $(wc -l packages) packages"
sleep 1

./run-build.sh packages "$NIXPKGS_PATH"
