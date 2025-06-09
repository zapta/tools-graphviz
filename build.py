"""A Python script to build the Graphviz package for a given platform"""

# This script is called from the github build workflow.


import os
import subprocess
from typing import List, Union
import argparse
import shutil
from pathlib import Path

# -- Command line options.
parser = argparse.ArgumentParser()


parser.add_argument("--platform_id", required=True, type=str, help="Platform to build")
parser.add_argument(
    "--package-tag", required=True, type=str, help="Package file name tag"
)
parser.add_argument(
    "--build-info-file", required=True, type=str, help="Text file with build properties"
)

args = parser.parse_args()


# -- Set the version of the upstream release.
# -- See list at https://graphviz.gitlab.io/download/
GRAPHVIZ_TAG = "12.1.2"


def run(cmd_args: Union[List[str], str], shell: bool = False) -> None:
    """Run a command and check that it succeeded. Select shell=true to enable
    shell features such as '*' glob."""
    print(f"\nRun: {cmd_args}")
    print(f"{shell=}")
    subprocess.run(cmd_args, check=True, shell=shell)
    print("Run done\n")


# @dataclass(frozen=True)
# class PlatformInfo:
#     """Represents the properties of a platform."""

#     graphviz_base_filename: str
#     graphviz_ext: str
#     # The name of the wrapper dir when uncompressing Graphviz package.
#     graphviz_wrapper_dir: str
#     unarchive_cmd: str


# # -- Maps apio platform codes to their attributes.
# PLATFORMS = {
#     "darwin-arm64": PlatformInfo(
#         f"graphviz-{GRAPHVIZ_TAG}-macOS",
#         "tar.gz",
#         f"graphviz-{GRAPHVIZ_TAG}-macOS",
#         ["tar", "zxf"],
#     ),
#     "darwin-x86-64": PlatformInfo(
#         f"graphviz-{GRAPHVIZ_TAG}-macOS",
#         "tar.gz",
#         f"graphviz-{GRAPHVIZ_TAG}-macOS",
#         ["tar", "zxf"],
#     ),
#     "linux-x86-64": PlatformInfo(
#         f"graphviz-{GRAPHVIZ_TAG}-linux-static-x86_64",
#         "tar.gz",
#         f"graphviz-{GRAPHVIZ_TAG}",
#         ["tar", "zxf"],
#     ),
#     "linux-aarch64": PlatformInfo(
#         f"graphviz-{GRAPHVIZ_TAG}-linux-static-arm64",
#         "tar.gz",
#         f"graphviz-{GRAPHVIZ_TAG}",
#         ["tar", "zxf"],
#     ),
#     "windows-amd64": PlatformInfo(
#         f"graphviz-{GRAPHVIZ_TAG}-win64",
#         "zip",
#         f"graphviz-{GRAPHVIZ_TAG}-win64",
#         ["unzip"],
#     ),
# }


def main():
    """Builds the Apio oss-cad-suite package for one platform."""

    # pylint: disable=too-many-statements

    # -- Print build parameters
    print("Apio oss-cad-suite builder")

    print("\nPARAMS:")
    print(f"  Platform ID:       {args.platform_id}")
    print(f"  Graphviz tag:       {GRAPHVIZ_TAG}")
    print(f"  Package tag:       {args.package_tag}")
    print(f"  Build info file:   {args.build_info_file}")

    # -- This build is for windows only.
    assert args.platform_id == "windows-amd64"

    # -- Map to Graphviz platform info
    # platform_info = PLATFORMS[args.platform_id]
    # print(f"\n{platform_info=}")

    # -- Determine if processing the windows package.
    # is_windows = "windows" in args.platform_id
    # print(f"\n{is_windows=}")

    # -- Save the start dir. It is assume to be at top of this repo.
    work_dir: Path = Path.cwd()
    print(f"\n{work_dir=}")

    # -- Save absolute build info file path
    build_info_path = Path(args.build_info_file).absolute()
    print(f"{build_info_path=}")
    assert build_info_path.exists()
    assert build_info_path.is_file()

    # --  Folder for storing the upstream packages
    upstream_dir: Path = work_dir / "_upstream" / args.platform_id
    print(f"\n{upstream_dir=}")
    upstream_dir.mkdir(parents=True, exist_ok=True)

    # -- Folder for storing the generated package file.
    package_dir: Path = work_dir / "_packages" / args.platform_id
    print(f"\n{package_dir=}")
    package_dir.mkdir(parents=True, exist_ok=True)

    # -- Construct target package file name
    parts = [
        "apio-graphviz",
        "-",
        args.platform_id,
        "-",
        args.package_tag,
        ".tar.gz",
    ]
    package_filename = "".join(parts)
    print(f"\n{package_filename=}")

    # Construct graphviz file name
    graphviz_fname = f"windows_10_cmake_Release_Graphviz-{GRAPHVIZ_TAG}-win64.zip"
    # graphviz_fname = (
    #     platform_info.graphviz_base_filename + "." + platform_info.graphviz_ext
    # )
    print(f"\n{graphviz_fname=}")

    # -- Construct Graphviz URL
    parts = [
        "https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/",
        "/",
        GRAPHVIZ_TAG,
        "/",
        graphviz_fname,
    ]
    graphviz_url = "".join(parts)
    print(f"\n{graphviz_url=}")

    # -- Download the Graphviz file.
    print(f"\nChanging to UPSTREAM_DIR: {str(upstream_dir)}")
    os.chdir(upstream_dir)
    print(f"\nDownloading {graphviz_url}")
    run(["wget", "-nv", graphviz_url])
    run(["ls", "-al"])

    # -- Uncompress the Graphviz archive
    print("Uncompressing the Graphviz file")
    run(["unzip", graphviz_fname])
    run(["ls", "-al", upstream_dir])

    # -- Delete the Graphviz archive, we don't need it anymore
    print("Deleting the Graphviz archive file")
    Path(graphviz_fname).unlink()
    run(["ls", "-al", upstream_dir])

    # -- Determine the root dir of the Graphviz files, below the
    # -- wrapper dir.
    print(f"\n{Path.cwd()=}")
    graphviz_root = upstream_dir / f"Graphviz-{GRAPHVIZ_TAG}-win64"
    print(f"{graphviz_root=}")

    # -- Copy the package files to the output directory.
    # -- We use rsync to copy all, including sim links, if any.
    # -- The does "/" matters.
    print("\nCopying package files.")
    run(["rsync", "-aq", f"{graphviz_root}/", f"{package_dir}/"])

    # -- Delete the upstream dir
    print(f"\nDeleting upstream dir {graphviz_root}")
    shutil.rmtree(graphviz_root)

    # -- Add to the the build info file and append platform info.
    package_build_info = package_dir / "BUILD-INFO"
    run(["cp", build_info_path, package_build_info])
    with package_build_info.open("a") as f:
        f.write(f"platform-id = {args.platform_id}\n")
        f.write(f"graphviz-tag = {GRAPHVIZ_TAG}\n")
    run(["ls", "-al", package_dir])
    run(["cat", "-n", package_build_info])

    # -- Compress the package. We run in a shell for the '*' glob to expand.
    print("Compressing the  package.")
    os.chdir(package_dir)
    run(f"tar zcf ../{package_filename} ./*", shell=True)

    # -- Delete the package dir
    print(f"\nDeleting package dir {package_dir}")
    shutil.rmtree(package_dir)

    # -- Final check
    os.chdir(work_dir)
    print(f"{Path.cwd()=}")
    run(["ls", "-al"])
    run(["ls", "-al", "_packages"])
    assert (Path("_packages") / package_filename).is_file()

    # -- All done


if __name__ == "__main__":
    main()
