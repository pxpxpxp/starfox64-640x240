# Star Fox 64 • Native 640×240 PVM

Private source and patch archive for **E01**, an experimental native 640×240 progressive build. It is not 480i, a 640×480 downconversion, or widescreen. Use normal **4:3** presentation and **8 MiB Expansion RAM**. NTSC only.

## Download and test

Apply [`Star_Fox_64_Native_640x240_PVM_E01.bps`](patches/Star_Fox_64_Native_640x240_PVM_E01.bps) to your own big-endian **Star Fox 64 (USA) (Rev 1)** dump with a BPS-compatible patcher.

- Clean base MD5: `741a94eee093c4c8684e66b89f8685e8`
- Patched SHA-256: `d8bfb05df6c6c62e2a70a8d6242a081d2b41aff0d90ee69a65b667431199ea98`
- Patch SHA-256: `1ad87798b25212068cf4c819006b9e84b715cc318c3911747e03842c1a1d017b`

Keep the original game and saves. Start with a separate test filename and copied save. Test title/menu, Corneria, HUD/text, pause/resume, transitions, audio, rumble and saving. On MiSTer use a compatible N64 core with Expansion Pak enabled; **no MiSTer Main modifications**.

## What changed

Logical 320×240 coordinates remain intact while the physical raster is 640×240. Changes cover expanded frame/depth buffers, progressive VI, viewports/scissors, 19 texture-rectangle paths including flipped derivatives, HUD/messages/stars/reset paths and correct build recompression dependencies. Offscreen texture rendering and logical projection remain unchanged. No new gameplay, save or rumble tuning is introduced. Existing textures are not repainted or upscaled assets.

The 14 actual modified source files are included under [`source-overlay/`](source-overlay/). The corresponding unified patch is [`patches/native-640x240-E01-source.patch`](patches/native-640x240-E01-source.patch). This is an overlay on a pinned, publicly available source baseline, not an incomplete claim of a standalone full tree.

## Reproduce from source

Linux prerequisites and official toolchain instructions are in the pinned [upstream README](https://github.com/sonicdcer/sf64/blob/4235c59f00b04440e3fd5fec49f0bc80e48cf212/README.md). This build used IDO 5.3, the pinned Torch tooling, MIPS binutils, Python requirements and CMake 3.x. Supply the game dump yourself; no ROM or extracted assets are included.

From this repository root:

```sh
git clone https://github.com/sonicdcer/sf64.git source
git -C source checkout --detach 4235c59f00b04440e3fd5fec49f0bc80e48cf212
git -C source submodule update --init --recursive
git -C source apply --check ../patches/native-640x240-E01-source.patch
git -C source apply ../patches/native-640x240-E01-source.patch
# Create/activate a Python virtual environment first.
python -m pip install -r source/tools/requirements-python.txt
# Copy your matching dump to source/baserom.us.rev1.z64.
make -C source toolchain
make -C source init VERSION=us REV=rev1 COMPARE=0 N_THREADS=4
sha256sum source/build/starfox64.us.rev1.z64
```

Apply the patch **once**; do not apply both patch and overlay. The overlay is provided for reading/review and should match the patched files. Full-source rebuild exactness was previously verified; future toolchain changes can affect reproducibility. [`docs/source-identity.json`](docs/source-identity.json) records source pins and overlay hashes.

## Validation

Fresh November 13 rechecks passed static rendering checks, baseline byte identity, 63 non-table DMA payloads, buffer bounds, independent CIC checksum and BPS reconstruction with all three CRCs. A fresh 6,500-VI software-RDP/LLE run exited cleanly, confirming actual 640×240 progressive VI, Corneria gameplay and repeated pause/resume. Evidence is under [`docs/`](docs/).

Validation uses Mupen64Plus, CXD4 low-level RSP and angrylion software RDP/VI. It is not hardware certification. **MiSTer/N64/PVM hardware, all stages/versus/endings, audio listening, physical rumble and save persistence remain unverified.** Twice the horizontal raster work may cause hardware slowdown; emulator speed is not a console benchmark.

For developer tests, keep this layout: `source/` patched checkout; `baseline/` a separate clean pinned checkout and build; `inputs/Star Fox 64 (USA) (Rev 1).z64` your clean dump. Then run:

```sh
python tests/test_render_conversion.py
python tests/verify_binary.py
python tests/check_cic.py
python tests/make_bps.py
```

The last command regenerates a root-level BPS and checks it independently; it does not overwrite the checked-in patch. `verify_binary.py` writes a root-level validation report. Build/test working trees and game data are ignored by Git.

See [`ATTRIBUTION.md`](ATTRIBUTION.md) for original authors and license boundaries. No ROM, extracted asset, emulator binary or raw memory dump is distributed.
