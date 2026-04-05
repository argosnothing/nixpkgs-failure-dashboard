{
  dart-sass,
  fetchPnpmDeps,
  jq,
  lib,
  makeBinaryWrapper,
  nodejs,
  pnpm_9,
  pnpmConfigHook,
  python3Packages,
  ripgrep,
  sqlite,
  stdenv,
}:
let
  version = "1.0.0";
  ui = stdenv.mkDerivation (finalAttrs: {
    inherit version;
    pname = "nixpkgs-failure-dashboard-frontend";

    src = ./.;

    nativeBuildInputs = [
      nodejs
      pnpm_9
      pnpmConfigHook
      dart-sass
    ];

    pnpmDeps = fetchPnpmDeps {
      pnpm = pnpm_9;
      inherit (finalAttrs) pname version src;
      fetcherVersion = 3;
      hash = "sha256-EfHyy2bLVIgE4E/JyN2pjsvrbNXT0Y0r0uVvTaYNabE=";
    };

    preBuild = ''
      substituteInPlace node_modules/sass-embedded/dist/lib/src/compiler-path.js \
        --replace-fail 'compilerCommand = (() => {' 'compilerCommand = (() => { return ["${lib.getExe dart-sass}"];'
    '';

    buildPhase = ''
      runHook preBuild

      pnpm build

      runHook postBuild
    '';

    installPhase = ''
      runHook preInstall

      mv dist $out

      runHook postInstall
    '';
  });
in
python3Packages.buildPythonApplication (finalAttrs: {
  inherit version;
  pname = "nixpkgs-failure-dashboard";
  pyproject = true;

  src = ./.;

  build-system = with python3Packages; [ hatchling ];

  dependencies = with python3Packages; [
    fastapi
    orjson
    sqlalchemy
    uvicorn
  ];

  nativeBuildInputs = [ makeBinaryWrapper ];

  postPatch = ''
    substituteInPlace app/config.py \
      --replace-fail 'DIST_BUILD_DIR = pathlib.Path("dist")' 'DIST_BUILD_DIR = pathlib.Path("${ui}")'

    substituteInPlace build-all-packages.sh \
      --replace-fail './collect-packages.nix' $out/share/collect-packages.nix
  '';

  postInstall = ''
    install -Dm 0755 build-all-packages.sh $out/bin/build-all-packages
    install -Dm 0755 run-build.sh $out/bin/run-build
    install -Dm 0644 collect-packages.nix $out/share/collect-packages.nix

    wrapProgram $out/bin/build-all-packages \
      --prefix PATH : ${
        lib.makeBinPath [
          jq
          ripgrep
          sqlite
        ]
      }
  '';

  meta = {
    description = "Better way to search and categorize build logs";
    homepage = "https://github.com/Sigmanificient/nixpkgs-failure-dashboard";
    license = lib.licenses.mit;
    mainProgram = "nixpkgs-failure-dashboard";
    platforms = lib.platforms.linux;
  };
})
