# LiteX: development platform for [PlatformIO](http://platformio.org)

Build automation for [LiteX](https://github.com/enjoy-digital/litex) boards, with a focus on RISC-V based soft cores. Still early development. 

# Installation
```
git clone https://github.com/long-pham/platform-litex.git
# install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

cd platform-litex/examples/hallo

# option 1: just try building the example
uv run pio run

# option 2: create .venv and run normal pio workflow
uv sync
pio run

```
# Usage

1. [Install PlatformIO](http://platformio.org)
2. Create PlatformIO project and configure a platform option in [platformio.ini](http://docs.platformio.org/page/projectconf.html) file:

## Stable version

```ini
[env:stable]
platform = litex_riscv
board = litex_vexriscv
framework = zephyr
...
```

## Development version

```ini
[env:development]
platform = https://github.com/hvegh/platform-litex.git
board = litex_vexriscv
framework = zephyr
...
```

# Configuration

Please navigate to [documentation TODO](http://docs.platformio.org/page/platforms/litex.html).
