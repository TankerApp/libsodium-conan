from conans import ConanFile, ConfigureEnvironment
import os
from os import path
from conans.tools import download, unzip, untargz, check_sha256

class SodiumConanFile(ConanFile):
    name        = "libsodium"
    version     = "1.0.11"
    description = "A modern and easy-to-use crypto library."
    branch      = "stable"
    license     = "ISC"
    url         = "https://github.com/paulobrizolara/libsodium-conan.git"  #recipe repo url
    repo_url    = "https://github.com/jedisct1/libsodium"                  #libsodium repo

    settings    = "os", "compiler", "arch"

    options = {
        "shared" : [True, False],
        "use_soname" : [True, False],
        "use_pie"    : [True, False, "Default"]
    }
    default_options = (
        "shared=False",
        "use_soname=True",
        "use_pie=Default"
    )

    BASE_URL_DOWNLOAD = "https://download.libsodium.org/libsodium/releases/"
    FILE_URL = BASE_URL_DOWNLOAD + "libsodium-1.0.11.tar.gz"
    EXTRACTED_FOLDER_NAME = "libsodium-1.0.11"
    FILE_SHA256 = 'a14549db3c49f6ae2170cbbf4664bd48ace50681045e8dbea7c8d9fb96f9c765'

    def source(self):
        zip_name = self.name + ".tar.gz"
        download(self.FILE_URL, zip_name)
        check_sha256(zip_name, self.FILE_SHA256)
        untargz(zip_name)

        #TODO: should verify the file signature (see https://download.libsodium.org/libsodium/content/installation)

    def build(self):
        self.prepare_build()
        self.configure_and_make()

    def package(self):
        #Copy all install dir content to the package directory
        self.copy("*", src=self.install_dir, dst=".")

    def package_info(self):
        self.cpp_info.libs = ["sodium"]


    ##################################################################################################

    def prepare_build(self):
        #Make install dir
        self.install_dir = path.abspath(path.join(".", "install"))
        self._try_make_dir(self.install_dir)

        #Change to extracted dir
        os.chdir(self.EXTRACTED_FOLDER_NAME)

    def configure_and_make(self):
        env = ConfigureEnvironment(self.deps_cpp_info, self.settings)
        self.run_configure(env)
        self.run("%s make" % env.command_line)
        self.run("%s make install" % env.command_line)

    def run_configure(self, env):
        options = self.make_configure_options()
        configure_file = path.join('.', 'configure')
        configure_cmd = "%s %s %s" % (env.command_line, configure_file, options)
        self.output.info(configure_cmd)

        self.run(configure_cmd)

    def make_configure_options(self):
        opts = [
            "--prefix=%s" % self.install_dir,

            self.autotools_bool_option("shared", self.options.shared),
            self.autotools_bool_option("static", not self.options.shared),
            self.autotools_bool_option("soname-versions", self.options.use_soname)
        ]

        if self.options.use_pie != "Default":
            opts.append(self.autotools_bool_option("pie", self.options.use_pie))

        return " ".join(opts)

    def autotools_bool_option(self, option_base_name, value):
        prefix = "--enable-" if value else "--disable-"

        return prefix + option_base_name


    def chmod_files(self, dir, mode):
        content = os.listdir(dir)

        for f in content:
            f = path.join(dir, f)

            if not path.isdir(f):
                os.chmod(f, mode)

    def _try_make_dir(self, dir):
        try:
            os.mkdir(dir)
        except OSError:
            #dir already exist
            pass
