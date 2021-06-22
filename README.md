# LiteX: development platform for [PlatformIO](http://platformio.org)

Build automation for [LiteX](https://github.com/enjoy-digital/litex) boards, with a focus on RISC-V based soft cores. Still early development. 

# Usage

1. [Install PlatformIO](http://platformio.org)
2. Create PlatformIO project and configure a platform option in [platformio.ini](http://docs.platformio.org/page/projectconf.html) file:

## Stable version

```ini
[env:stable]
platform = litex
board = ...
...
```

## Development version

```ini
[env:development]
platform = https://github.com/hvegh/platform-litex.git
board = ...
...
```

# Configuration

Please navigate to [documentation TODO](http://docs.platformio.org/page/platforms/litex.html).
