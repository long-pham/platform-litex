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

import copy
import os
import platform

from platformio.managers.platform import PlatformBase
from platformio.util import get_systype


class Litex_riscvPlatform(PlatformBase):

    def configure_default_packages(self, variables, targets):
        if "zephyr" in variables.get("pioframework", []):
            for p in self.packages:
                if p.startswith("framework-zephyr-") or p in (
                        "tool-cmake",
                        "tool-dtc",
                        "tool-ninja"
                ):
                    self.packages[p]["optional"] = False
            if "windows" not in get_systype():
                self.packages["tool-gperf"]["optional"] = False

        return PlatformBase.configure_default_packages(self, variables, targets)


    def get_boards(self, id_=None):
        result = PlatformBase.get_boards(self, id_)
        if not result:
            return result
        if id_:
            return self._add_default_debug_tools(result)
        else:
            for key, value in result.items():
                result[key] = self._add_default_debug_tools(result[key])
        return result

    def _add_default_debug_tools(self, board):
        debug = board.manifest.get("debug", {})
        if "tools" not in debug:
            debug["tools"] = {}

        tools = (
            "jlink",
            "qemu",
            "ftdi",
            "minimodule",
            "olimex-arm-usb-tiny-h",
            "olimex-arm-usb-ocd-h",
            "olimex-arm-usb-ocd",
            "olimex-jtag-tiny",
            "verilator"
        )
        for tool in tools:
            if tool in debug["tools"]:
                continue

        board.manifest["debug"] = debug
        return board
