{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs.python311Packages; [
    pandas
    beautifulsoup4
    requests
    openpyxl
    nltk
  ];

  shellHook = ''
    echo "Python 3.11 development environment is ready."
  '';
}
