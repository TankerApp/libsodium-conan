from conans import ConanFile, AutoToolsBuildEnvironment
import os
from os import path
import multiprocessing
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
        env = AutoToolsBuildEnvironment(self)
        configure_args = self.get_configure_args()
        print("./configure", " ".join(configure_args))
        env.configure(args=configure_args)
        env.make(args=["-j", str(multiprocessing.cpu_count())])
        env.make(args=["install"])

    def get_configure_args(self):
        args = [
            "--prefix=%s" % self.install_dir,

            self.autotools_bool_arg("shared", self.options.shared),
            self.autotools_bool_arg("static", not self.options.shared),
            self.autotools_bool_arg("soname-versions", self.options.use_soname)
        ]

        if self.options.use_pie != "Default":
            args.append(self.autotools_bool_option("pie", self.options.use_pie))

        return args

    def autotools_bool_arg(self, arg_base_name, value):
        prefix = "--enable-" if value else "--disable-"

        return prefix + arg_base_name


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
