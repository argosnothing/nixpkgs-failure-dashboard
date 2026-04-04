{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = {
    self,
    nixpkgs,
  }: let
    inherit (nixpkgs) lib;

    applySystems = lib.genAttrs ["x86_64-linux"];
    forAllSystems = f:
      applySystems (system: f nixpkgs.legacyPackages.${system});
  in {
    formatter = forAllSystems (pkgs: pkgs.alejandra);

    devShells = forAllSystems (pkgs: let
      py-env = pkgs.python3.withPackages (p: [p.hatchling]);
    in {
      default = pkgs.mkShell {
        packages = with pkgs; [
          jq
          ripgrep
          py-env
          sqlite
          nodejs
          pnpm
        ];
      };
    });

    packages = forAllSystems (pkgs: {
      default = pkgs.callPackage ./default.nix {};
    });
  };
}
