{
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = {
    self,
    nixpkgs,
  }: let
    inherit (nixpkgs) lib;

    applySystems = lib.genAttrs ["x86_64-linux"];
    forAllSystems = f:
      applySystems (
        system:
          f (import nixpkgs {
            inherit system;
            config = {
              android_sdk.accept_license = true;
              allowUnfree = true;
            };
          })
      );
  in {
    formatter = forAllSystems (pkgs: pkgs.alejandra);

    devShells = forAllSystems (pkgs: let
      py-env = pkgs.python3.withPackages (
        p: [
          p.fastapi
          p.fastapi-cli
        ]
      );
    in {
      default = pkgs.mkShell {
        packages = with pkgs; [
          py-env
        ];
      };
    });
  };
}
