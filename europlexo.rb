class Europlexo < Formula
  include Language::Python::Virtualenv

  desc "A command line script for downloading tv series"
  homepage "https://github.com/Mortafix/homebrew-EuroPlexo"
  url "https://github.com/Mortafix/homebrew-EuroPlexo/archive/v1.2.3.tar.gz"
  sha256 "3e1730ad838b62eb2994607ce0acaf19f270795a59fe2df2a87e61bf9ed1faad"
  version "1.2.3"

  depends_on "youtube-dl"
  depends_on "python3"

  bottle :unneeded

  resource "soupsieve" do
    url "https://files.pythonhosted.org/packages/3e/db/5ba900920642414333bdc3cb397075381d63eafc7e75c2373bbc560a9fa1/soupsieve-2.0.1.tar.gz"
    sha256 "a59dc181727e95d25f781f0eb4fd1825ff45590ec8ff49eadfd7f1a537cc0232"
  end

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/c6/62/8a2bef01214eeaa5a4489eca7104e152968729512ee33cb5fbbc37a896b7/beautifulsoup4-4.9.1.tar.gz"
    sha256 "73cc4d115b96f79c7d77c1c7f7a0a8d4c57860d1041df407dd1aae7f07a77fd7"
  end

  resource "bs4" do
    url "https://files.pythonhosted.org/packages/10/ed/7e8b97591f6f456174139ec089c769f89a94a1a4025fe967691de971f314/bs4-0.0.1.tar.gz"
    sha256 "36ecea1fd7cc5c0c6e4a1ff075df26d50da647b75376626cc186e2212886dd3a"
  end

  resource "certifi" do
  	url "https://files.pythonhosted.org/packages/40/a7/ded59fa294b85ca206082306bba75469a38ea1c7d44ea7e1d64f5443d67a/certifi-2020.6.20.tar.gz"
  	sha256 "5930595817496dd21bb8dc35dad090f1c2cd0adfaf21204bf6732ca5d8ee34d3"
  end

  resource "chardet" do
    url "https://files.pythonhosted.org/packages/fc/bb/a5768c230f9ddb03acc9ef3f0d4a3cf93462473795d18e9535498c8f929d/chardet-3.0.4.tar.gz"
    sha256 "84ab92ed1c4d4f16916e05906b6b75a6c0fb5db821cc65e70cbd64a3e2a5eaae"
  end

  resource "pyparsing" do
    url "https://files.pythonhosted.org/packages/c1/47/dfc9c342c9842bbe0036c7f763d2d6686bcf5eb1808ba3e170afdb282210/pyparsing-2.4.7.tar.gz"
    sha256 "c203ec8783bf771a155b207279b9bccb8dea02d8f0c9e5f8ead507bc3246ecc1"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/ea/b7/e0e3c1c467636186c39925827be42f16fee389dc404ac29e930e9136be70/idna-2.10.tar.gz"
    sha256 "b307872f855b18632ce0c21c5e45be78c0ea7ae4c15c828c20788b26921eb3f6"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/81/f4/87467aeb3afc4a6056e1fe86626d259ab97e1213b1dfec14c7cb5f538bf0/urllib3-1.25.10.tar.gz"
    sha256 "91056c15fa70756691db97756772bb1eb9678fa585d9184f24534b100dc60f4a"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/da/67/672b422d9daf07365259958912ba533a0ecab839d4084c487a5fe9a5405f/requests-2.24.0.tar.gz"
    sha256 "b3559a131db72c33ee969480840fff4bb6dd111de7dd27c8ee1f820f4f00231b"
  end

  resource "requests-toolbelt" do
    url "https://files.pythonhosted.org/packages/28/30/7bf7e5071081f761766d46820e52f4b16c8a08fef02d2eb4682ca7534310/requests-toolbelt-0.9.1.tar.gz"
    sha256 "968089d4584ad4ad7c171454f0a5c6dac23971e9472521ea3b6d49d610aa6fc0"
  end

  resource "cloudscraper" do
    url "https://files.pythonhosted.org/packages/e3/67/12931f5b2128034461e8b6ebce38073d29017442ff9d0154f5c88f15e1ae/cloudscraper-1.2.46.tar.gz"
    sha256 "793095bbc37aae84a5c38d9f66b56f3c83a00f0b1ff2d334f75a2b8f88b924af"
  end

  resource "emoji" do
  	url "https://files.pythonhosted.org/packages/ff/1c/1f1457fe52d0b30cbeebfd578483cedb3e3619108d2d5a21380dfecf8ffd/emoji-0.6.0.tar.gz"
  	sha256 "e42da4f8d648f8ef10691bc246f682a1ec6b18373abfd9be10ec0b398823bd11"
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
