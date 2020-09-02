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
    url "https://files.pythonhosted.org/packages/3e/db/5ba900920642414333bdc3cb397075381d63eafc7e75c2373bbc560a9fa1/soupsieve-2.0.1.tar.gz#sha256=a59dc181727e95d25f781f0eb4fd1825ff45590ec8ff49eadfd7f1a537cc0232"
    sha256 "a59dc181727e95d25f781f0eb4fd1825ff45590ec8ff49eadfd7f1a537cc0232"
  end

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/c6/62/8a2bef01214eeaa5a4489eca7104e152968729512ee33cb5fbbc37a896b7/beautifulsoup4-4.9.1.tar.gz#sha256=73cc4d115b96f79c7d77c1c7f7a0a8d4c57860d1041df407dd1aae7f07a77fd7"
    sha256 "73cc4d115b96f79c7d77c1c7f7a0a8d4c57860d1041df407dd1aae7f07a77fd7"
  end

  resource "bs4" do
    url "https://files.pythonhosted.org/packages/10/ed/7e8b97591f6f456174139ec089c769f89a94a1a4025fe967691de971f314/bs4-0.0.1.tar.gz#sha256=36ecea1fd7cc5c0c6e4a1ff075df26d50da647b75376626cc186e2212886dd3a"
    sha256 "36ecea1fd7cc5c0c6e4a1ff075df26d50da647b75376626cc186e2212886dd3a"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/5e/c4/6c4fe722df5343c33226f0b4e0bb042e4dc13483228b4718baf286f86d87/certifi-2020.6.20-py2.py3-none-any.whl#sha256=8fc0819f1f30ba15bdb34cceffb9ef04d99f420f68eb75d901e9560b8749fc41"
    sha256 "8fc0819f1f30ba15bdb34cceffb9ef04d99f420f68eb75d901e9560b8749fc41"
  end

  resource "chardet" do
    url "https://files.pythonhosted.org/packages/bc/a9/01ffebfb562e4274b6487b4bb1ddec7ca55ec7510b22e4c51f14098443b8/chardet-3.0.4-py2.py3-none-any.whl#sha256=fc323ffcaeaed0e0a02bf4d117757b98aed530d9ed4531e3e15460124c106691"
    sha256 "fc323ffcaeaed0e0a02bf4d117757b98aed530d9ed4531e3e15460124c106691"
  end

  resource "pyparsing" do
    url "https://files.pythonhosted.org/packages/8a/bb/488841f56197b13700afd5658fc279a2025a39e22449b7cf29864669b15d/pyparsing-2.4.7-py2.py3-none-any.whl#sha256=ef9d7589ef3c200abe66653d3f1ab1033c3c419ae9b9bdb1240a85b024efc88b"
    sha256 "ef9d7589ef3c200abe66653d3f1ab1033c3c419ae9b9bdb1240a85b024efc88b"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/a2/38/928ddce2273eaa564f6f50de919327bf3a00f091b5baba8dfa9460f3a8a8/idna-2.10-py2.py3-none-any.whl#sha256=b97d804b1e9b523befed77c48dacec60e6dcb0b5391d57af6a65a312a90648c0"
    sha256 "b97d804b1e9b523befed77c48dacec60e6dcb0b5391d57af6a65a312a90648c0"
  end

  resource "urllib3" do
    url "https://files.pythonhosted.org/packages/9f/f0/a391d1463ebb1b233795cabfc0ef38d3db4442339de68f847026199e69d7/urllib3-1.25.10-py2.py3-none-any.whl#sha256=e7983572181f5e1522d9c98453462384ee92a0be7fac5f1413a1e35c56cc0461"
    sha256 "e7983572181f5e1522d9c98453462384ee92a0be7fac5f1413a1e35c56cc0461"
  end

  resource "requests" do
    url "https://files.pythonhosted.org/packages/45/1e/0c169c6a5381e241ba7404532c16a21d86ab872c9bed8bdcd4c423954103/requests-2.24.0-py2.py3-none-any.whl#sha256=fe75cc94a9443b9246fc7049224f75604b113c36acb93f87b80ed42c44cbb898"
    sha256 "fe75cc94a9443b9246fc7049224f75604b113c36acb93f87b80ed42c44cbb898"
  end

  resource "requests-toolbelt" do
    url "https://files.pythonhosted.org/packages/60/ef/7681134338fc097acef8d9b2f8abe0458e4d87559c689a8c306d0957ece5/requests_toolbelt-0.9.1-py2.py3-none-any.whl#sha256=380606e1d10dc85c3bd47bf5a6095f815ec007be7a8b69c878507068df059e6f"
    sha256 "380606e1d10dc85c3bd47bf5a6095f815ec007be7a8b69c878507068df059e6f"
  end

  resource "cloudscraper" do
    url "https://files.pythonhosted.org/packages/93/1b/5b08eadf5e7aa1ae8bf1bdc54e23e8fab1801b8f7dbc9569ace05c943b6c/cloudscraper-1.2.46-py2.py3-none-any.whl#sha256=a7ae28b5dc4e4ef0789ef608c42a4382bf6d3e3dd6b8117c2e3633103131ae43"
    sha256 "a7ae28b5dc4e4ef0789ef608c42a4382bf6d3e3dd6b8117c2e3633103131ae43"
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
