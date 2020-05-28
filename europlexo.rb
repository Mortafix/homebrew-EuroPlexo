class EuroPlexo < Formula

  include Language::Python::Virtualenv

  desc "A command line script for downloading tv series"
  homepage "https://github.com/Mortafix/EuroPlexo"
  url "https://github.com/Mortafix/EuroPlexo/archive/v1.0.0.tar.gz"
  sha256 ""
  version "1.0.0"

  depends_on "youtube-dl"

  bottle :unneeded

  def install
    virtualenv_install_with_resources
  end
end