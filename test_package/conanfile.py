from conans import ConanFile, CMake
import os
from os import path
from shutil import copyfile

username = os.getenv("CONAN_USERNAME", "paulobrizolara")
channel = os.getenv("CONAN_CHANNEL", "testing")
package_name = "libsodium"
version = "1.0.11"

class PackageTest(ConanFile):
    settings = "os", "compiler", "arch"
    requires = "%s/%s@%s/%s" % (package_name, version, username, channel)
    generators = "cmake"
    default_options = ""

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake %s %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)
        
    def test(self):
        exec_path = path.join('bin', 'example')
        self.output.info("running test: " + exec_path)
        self.run(exec_path)

    def _try_make_dir(self, dir):
        try:
            os.mkdir(dir)
        except OSError:
            #dir already exist
            pass
