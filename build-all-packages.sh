#!/usr/bin/env bash
NIXPKGS_PATH=$(nix eval --impure --expr '
  let url = "https://github.com/NixOS/nixpkgs/archive/master.tar.gz";
  in (fetchTarball { inherit url; })' | tr -d '"')

nix eval --impure  --json --expr "
  (import ./collect-packages.nix) { pkgs = import $NIXPKGS_PATH {}; }
" -vv > packages.json

cat packages.json | tr -d '["]' | tr ',' '\n' > packages

echo "starting build of $(wc -l packages) packages"
sleep 1

./run-build.sh packages "$NIXPKGS_PATH"
