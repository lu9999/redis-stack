from . import Recipe
from ..config import Config
from ..paths import Paths
from ..components.nodejs import NodeJS
import os
import shutil
from loguru import logger


class RedisInsightBase(Recipe):
    def __init__(self, osnick, arch="x86_64", osname="Linux"):
        self.OSNICK = osnick
        self.ARCH = arch
        self.OSNAME = osname
        self.__PATHS__ = Paths(self.PACKAGE_NAME, osnick, arch, osname)
        self.C = Config()

    @property
    def __package_base_args__(self) -> list:
        """Return base arguments for the package."""
        c = Config()
        return [
            "fpm",
            "-s dir",
            f"-C {self.__PATHS__.WORKDIR}",
            f"-n {c.get_key(self.PACKAGE_NAME)['product']}",
            f"--architecture {self.ARCH}",
            f"--vendor '{c.get_key('vendor')}'",
            f"--version {self.version}",
            f"--url '{c.get_key('url')}'",
            f"--license '{c.get_key('license')}'",
            "--category server",
            f"--maintainer '{c.get_key('email')}'",
            f"--description '{c.get_key(self.PACKAGE_NAME)['description']}'",
            "--directories /opt/redis-stack",
        ]

    def deb(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.deb"
        )
        fpmargs.append(f"--deb-user {self.C.get_key('product_user')}")
        fpmargs.append(f"--deb-group {self.C.get_key('product_group')}")
        fpmargs.append(f"--deb-dist {distribution}")
        fpmargs.append("-t deb")

        if not os.path.isdir(self.__PATHS__.SVCDIR):
            os.makedirs(self.__PATHS__.SVCDIR)

        for i in [
            "redisinsight.service",
        ]:
            shutil.copyfile(
                os.path.join(self.__PATHS__.SCRIPTDIR, "services", i),
                os.path.join(self.__PATHS__.SVCDIR, i),
            )
            fpmargs.append(f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, i))}")

        return fpmargs

    def rpm(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.rpm"
        )
        fpmargs.append(f"--rpm-user {self.C.get_key('product_user')}")
        fpmargs.append(f"--rpm-group {self.C.get_key('product_group')}")
        fpmargs.append(f"--rpm-dist {distribution}")
        fpmargs.append("-t rpm")

        if not os.path.isdir(self.__PATHS__.SVCDIR):
            os.makedirs(self.__PATHS__.SVCDIR)

        for i in [
            "redisinsight.service",
        ]:
            shutil.copyfile(
                os.path.join(self.__PATHS__.SCRIPTDIR, "services", i),
                os.path.join(self.__PATHS__.SVCDIR, i),
            )
            fpmargs.append(f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, i))}")
        return fpmargs

    def pacman(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.{self.ARCH}.pacman"
        )
        fpmargs.append(f"--pacman-user {self.C.get_key('product_user')}")
        fpmargs.append(f"--pacman-group {self.C.get_key('product_group')}")
        fpmargs.append("--pacman-compression gz")
        fpmargs.append("-t pacman")

        if not os.path.isdir(self.__PATHS__.SVCDIR):
            os.makedirs(self.__PATHS__.SVCDIR)
        for i in [
            "redisinsight.service",
        ]:
            shutil.copyfile(
                os.path.join(self.__PATHS__.SCRIPTDIR, "services", i),
                os.path.join(self.__PATHS__.SVCDIR, i),
            )
            fpmargs.append(f"--config-files {(os.path.join(self.__PATHS__.SVCDIR, i))}")

        return fpmargs

    def osxpkg(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.osxpkg"
        )
        fpmargs.append("-t osxpkg")
        return fpmargs

    def zip(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.zip"
        )
        return fpmargs

    def tar(self, fpmargs, distribution):
        fpmargs.append(
            f"-p {self.C.get_key(self.PACKAGE_NAME)['product']}-{self.version}.{distribution}.tar.gz"
        )
        return fpmargs

    def package(
        self,
        package_type: str = "deb",
        distribution: str = "bionic",
    ):

        logger.info(f"Building {package_type} package")
        fpmargs = self.__package_base_args__

        if package_type == "deb":
            fpmargs = self.deb(fpmargs, distribution)

        elif package_type == "rpm":
            fpmargs = self.rpm(fpmargs, distribution)

        elif package_type == "osxpkg":
            fpmargs = self.osxpkg(fpmargs, distribution)

        elif package_type == "pacman":
            fpmargs = self.pacman(fpmargs, distribution)
        elif package_type == "zip":  # ignored
            fpmargs = self.zip(fpmargs, distribution)
        elif package_type == "tar":  # ignored
            fpmargs = self.tar(fpmargs, distribution)
        else:
            raise AttributeError(f"{package_type} is an invalid package type")

        cmd = " ".join(fpmargs)
        logger.debug(f"Packaging: {cmd}")
        return os.system(cmd)


class RedisInsight(RedisInsightBase):
    """A recipe to build a redisinsight package from the native app"""

    PACKAGE_NAME = "redisinsight"

    def prepackage(
        self, binary_dir: str, ignore: bool = False, version_override: str = None
    ):

        raise NotImplementedError("DISABLED FOR NOW, INTENTIONALY.")
        for i in [
            self.__PATHS__.EXTERNAL,
            self.__PATHS__.DESTDIR,
            self.__PATHS__.LIBDIR,
            self.__PATHS__.BINDIR,
            self.__PATHS__.SHAREDIR,
        ]:
            os.makedirs(i, exist_ok=True, mode=0o755)

        from ..components.redisinsight import RedisInsight as RI

        for i in [NodeJS, RI]:
            n = i(self.PACKAGE_NAME, self.OSNICK, self.ARCH, self.OSNAME)
            n.prepare()


class RedisInsightWeb(RedisInsightBase):
    """A recipe to build a redisinsight package for the web application"""

    PACKAGE_NAME = "redisinsight-web"

    def prepackage(
        self, binary_dir: str, ignore: bool = False, version_override: str = None
    ):

        for i in [
            self.__PATHS__.EXTERNAL,
            self.__PATHS__.DESTDIR,
            self.__PATHS__.LIBDIR,
            self.__PATHS__.BINDIR,
            self.__PATHS__.SHAREDIR,
        ]:
            os.makedirs(i, exist_ok=True, mode=0o755)

        from ..components.redisinsight import RedisInsightWeb as RI

        for i in [NodeJS, RI]:
            n = i(self.PACKAGE_NAME, self.OSNICK, self.ARCH, self.OSNAME)
            n.prepare()
