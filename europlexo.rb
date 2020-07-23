class Europlexo < Formula

  include Language::Python::Virtualenv

  desc "A command line script for downloading tv series"
  homepage "https://github.com/Mortafix/homebrew-EuroPlexo"
  url "https://github.com/Mortafix/homebrew-EuroPlexo/archive/v1.2.0.tar.gz"
  sha256 "c6c7e5ba79684de824cdfbdb307d46d92a6c076a0b9e8e4193c9048103d662db"
  version "1.2.0"

  depends_on "youtube-dl"

  bottle :unneeded

  resource "requests" do
    url "https://files.pythonhosted.org/packages/f5/4f/280162d4bd4d8aad241a21aecff7a6e46891b905a4341e7ab549ebaf7915/requests-2.23.0.tar.gz"
    sha256 "b3f43d496c6daba4493e7c431722aeb7dbc6288f52a6e04e7b6023b0247817e6"
  end

  resource "bs4" do
    url "https://files.pythonhosted.org/packages/10/ed/7e8b97591f6f456174139ec089c769f89a94a1a4025fe967691de971f314/bs4-0.0.1.tar.gz"
    sha256 "36ecea1fd7cc5c0c6e4a1ff075df26d50da647b75376626cc186e2212886dd3a"
  end

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/c6/62/8a2bef01214eeaa5a4489eca7104e152968729512ee33cb5fbbc37a896b7/beautifulsoup4-4.9.1.tar.gz"
    sha256 "73cc4d115b96f79c7d77c1c7f7a0a8d4c57860d1041df407dd1aae7f07a77fd7"
  end

  resource "soupsieve" do
    url "https://files.pythonhosted.org/packages/3e/db/5ba900920642414333bdc3cb397075381d63eafc7e75c2373bbc560a9fa1/soupsieve-2.0.1.tar.gz"
    sha256 "a59dc181727e95d25f781f0eb4fd1825ff45590ec8ff49eadfd7f1a537cc0232"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/b8/e2/a3a86a67c3fc8249ed305fc7b7d290ebe5e4d46ad45573884761ef4dea7b/certifi-2020.4.5.1.tar.gz"
    sha256 "51fcb31174be6e6664c5f69e3e1691a2d72a1a12e90f872cbdb1567eb47b6519"
  end

  resource "chardet" do
    url "https://files.pythonhosted.org/packages/fc/bb/a5768c230f9ddb03acc9ef3f0d4a3cf93462473795d18e9535498c8f929d/chardet-3.0.4.tar.gz"
    sha256 "84ab92ed1c4d4f16916e05906b6b75a6c0fb5db821cc65e70cbd64a3e2a5eaae"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/cb/19/57503b5de719ee45e83472f339f617b0c01ad75cba44aba1e4c97c2b0abd/idna-2.9.tar.gz"
    sha256 "7588d1c14ae4c77d74036e8c22ff447b26d0fde8f007354fd48a7814db15b7cb"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/05/8c/40cd6949373e23081b3ea20d5594ae523e681b6f472e600fbc95ed046a36/urllib3-1.25.9.tar.gz"
    sha256 "3018294ebefce6572a474f0604c2021e33b3fd8006ecd11d62107a5d2a963527"
  end

  require "fileutils"

  def install
    ENV.append "CPPFLAGS", "-I#{MacOS.sdk_path_if_needed}/usr/include/ffi"

    # Installing python modules
    venv = virtualenv_create(libexec, Formula["python3"].opt_bin/"python3")
    venv.pip_install resources

    # My python dependencies
    (libexec/"bin").install "config.json"
    (libexec/"bin").install "ScanFolder.py"
    (libexec/"bin").install "LinkFinder.py"
    (libexec/"bin").install "SeriesFinder.py"
    (libexec/"bin"/"dispatcher").install "dispatcher/DeltaBit.py"
    (libexec/"bin"/"dispatcher").install "dispatcher/TurboVid.py"

    # Final Script
    (libexec/"bin").install "EuroPlexo.py" => "europlexo"
    FileUtils.chmod("+x", libexec/"bin/europlexo")
    (bin/"europlexo").write_env_script libexec/"bin/europlexo", :PATH => "#{libexec}/bin:$PATH"
  end

  test do
    system "europlexo -h"
  end
end