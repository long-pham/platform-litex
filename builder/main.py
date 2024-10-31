# Copyright 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
from platform import system
from os import makedirs
from os.path import isdir, join

from SCons.Script import (
    ARGUMENTS,
    COMMAND_LINE_TARGETS,
    AlwaysBuild,
    Builder,
    Default,
    DefaultEnvironment,
    WhereIs
)

def generate_vh(target, source, env):
    binary_file = source[0].get_path()
    assert binary_file.endswith(".bin")
    vh_file = binary_file.replace(".bin", ".vh")
    result = ""
    with open(binary_file, "rb") as fp:
        cnt = 7
        s = ["00"] * 8
        while True:
            data = fp.read(1)
            if not data:
                result = result + "".join(s) + "\n"
                break
            s[cnt] = "{:02X}".format(data[0])
            if cnt == 0:
                result = result + "".join(s) + "\n"
                s = ["00"] * 8
                cnt = 8
            cnt -= 1

    with open(vh_file, "wb") as fp:
        fp.write(bytes(result, "ascii"))


env = DefaultEnvironment()
env.SConscript("compat.py", exports="env")
platform = env.PioPlatform()
board_config = env.BoardConfig()

# env.Replace(
#     AR="riscv64-zephyr-elf-gcc-ar",
#     AS="riscv64-zephyr-elf-as",
#     CC="riscv64-unknown-elf-gcc",
#     GDB="riscv64-zephyr-elf-gdb",
#     CXX="riscv64-zephyr-elf-g++",
#     OBJCOPY="riscv64-zephyr-elf-objcopy",
#     RANLIB="riscv64-zephyr-elf-gcc-ranlib",
#     SIZETOOL="riscv64-zephyr-elf-size",

#     ARFLAGS=["rc"],

#     SIZEPRINTCMD='$SIZETOOL -d $SOURCES',

#     PROGSUFFIX=".elf"
# )


# Allow user to override via pre:script
if env.get("PROGNAME", "program") == "program":
    env.Replace(PROGNAME="firmware")

env.Append(
    BUILDERS=dict(
        ElfToHex=Builder(
            action=env.VerboseAction(
                " ".join([ "$OBJCOPY", "-O", "ihex", "$SOURCES", "$TARGET" ]),
                "Building $TARGET"
            ),
            suffix=".hex"
        ),
        ElfToBin=Builder(
            action=env.VerboseAction(
                " ".join(["$OBJCOPY", "-O", "binary", "$SOURCES", "$TARGET"]),
                "Building $TARGET",
            ),
            suffix=".bin",
        ),
        BinToVh=Builder(action=env.VerboseAction(generate_vh, "Building $TARGET"),
            suffix=".vh"
        ),
    )
)

pioframework = env.get("PIOFRAMEWORK", [])

if not pioframework:
    env.SConscript("frameworks/_bare.py", exports="env")

#
# Target: Build executable and linkable firmware
#

if "zephyr" in pioframework:
    env.SConscript(
        join(platform.get_package_dir("framework-zephyr"),
            "scripts", "platformio", "platformio-build-pre.py"),
        exports={"env": env}
    )

target_elf = None
if "nobuild" in COMMAND_LINE_TARGETS:
    target_elf = join("$BUILD_DIR", "${PROGNAME}.elf")
    target_bin = join("$BUILD_DIR", "${PROGNAME}.bin")
    target_hex = join("$BUILD_DIR", "${PROGNAME}.hex")
    target_vh  = join("$BUILD_DIR", "${PROGNAME}.vh")
else:
    target_elf = env.BuildProgram()
    target_hex = env.ElfToHex(join("$BUILD_DIR", "${PROGNAME}"), target_elf)
    target_bin = env.ElfToBin(join("$BUILD_DIR", "${PROGNAME}"), target_elf)
    target_hex = env.BinToVh(join("$BUILD_DIR", "${PROGNAME}"), target_bin)

AlwaysBuild(env.Alias("nobuild", target_hex))
target_buildprog = env.Alias("buildprog", target_hex, target_hex)

#
# Target: Print binary size
#

target_size = env.Alias(
    "size", target_elf,
    env.VerboseAction("$SIZEPRINTCMD", "Calculating size $SOURCE"))
AlwaysBuild(target_size)

#
# Target: Upload by default .bin file
#

upload_protocol = env.subst("$UPLOAD_PROTOCOL")
debug_tools = board_config.get("debug.tools", {})
upload_actions = []
upload_target = target_elf

if upload_protocol.startswith("jlink"):

    def _jlink_cmd_script(env, source):
        build_dir = env.subst("$BUILD_DIR")
        if not isdir(build_dir):
            makedirs(build_dir)
        script_path = join(build_dir, "upload.jlink")
        commands = [
            "h",
            "loadfile %s" % source,
            "r",
            "q"
        ]
        with open(script_path, "w") as fp:
            fp.write("\n".join(commands))
        return script_path

    env.Replace(
        __jlink_cmd_script=_jlink_cmd_script,
        UPLOADER="JLink.exe" if system() == "Windows" else "JLinkExe",
        UPLOADERFLAGS=[
            "-device", env.BoardConfig().get("debug", {}).get("jlink_device"),
            "-speed", env.GetProjectOption("debug_speed", "4000"),
            "-if", "JTAG",
            "-jtagconf", "-1,-1",
            "-autoconnect", "1",
            "-NoGui", "1"
        ],
        UPLOADCMD='$UPLOADER $UPLOADERFLAGS -CommanderScript "${__jlink_cmd_script(__env__, SOURCE)}"'
    )
    upload_target = target_hex
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

elif upload_protocol in debug_tools:
    if upload_protocol == "renode":
        uploader = "renode"
        tool_args = [arg for arg in debug_tools.get(upload_protocol).get(
            "server").get("arguments", []) if arg != "--disable-xwt"]
        tool_args.extend([
            "-e", "sysbus LoadELF @$SOURCE",
            "-e", "start"
        ])
    else:
        uploader = "openocd"
        tool_args = [
            "-c",
            "debug_level %d" % (2 if int(ARGUMENTS.get("PIOVERBOSE", 0)) else 1),
            "-s", platform.get_package_dir("tool-openocd-riscv") or ""
        ]
        tool_args.extend(
            debug_tools.get(upload_protocol).get("server").get("arguments", []))
        if env.GetProjectOption("debug_speed"):
            tool_args.extend(
                ["-c", "adapter_khz %s" % env.GetProjectOption("debug_speed")]
            )
        tool_args.extend([
            "-c", "program {$SOURCE} %s verify; shutdown;" %
            board_config.get("upload").get("flash_start", "")
        ])
    env.Replace(
        UPLOADER=uploader,
        UPLOADERFLAGS=tool_args,
        UPLOADCMD="$UPLOADER $UPLOADERFLAGS"
    )
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

# custom upload tool
elif upload_protocol == "custom":
    upload_actions = [env.VerboseAction("$UPLOADCMD", "Uploading $SOURCE")]

else:
    sys.stderr.write("Warning! Unknown upload protocol %s\n" % upload_protocol)

#AlwaysBuild(env.Alias("upload", upload_target, upload_actions))


#
# Setup default targets
#

Default([target_buildprog, target_size])
