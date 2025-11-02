# oc-amd-patcher

A powerful and fully automated Python utility for applying **AMD Vanilla OpenCore kernel patches** directly into your `config.plist`. It supports **release**, **beta**, and **custom patch files**, along with detailed logging and a quiet mode for automation scripts.

---

## Installation

```bash
git clone https://github.com/itsmaclol/oc-amd-patcher-cli.git
cd oc-amd-patcher-cli
chmod +x oc_amd_patch_auto.py
```

###Make sure Python 3.7+ is installed
---

## Usage

### Basic Usage (Release Patches)
Automatically downloads and applies the latest **release** patches from the official AMD Vanilla repo:

```bash
python3 oc_amd_patch_auto.py --config /path/to/config.plist --cores X
```

**What it does:**
- Downloads the release patches from the `master` branch.
- Wipes all existing `Kernel -> Patch` entries.
- Inserts the new patches.
- Sets `ProvideCurrentCpuInfo = True`.

---

### 🔹 Beta Patches Mode
Downloads and applies the **beta** patches from the AMD Vanilla `beta` branch:

```bash
python3 oc_amd_patch_auto.py --config /path/to/config.plist --beta --cores X
```

**Source:**
```
https://raw.githubusercontent.com/AMD-OSX/AMD_Vanilla/refs/heads/beta/patches.plist
```

---

### 🔹 Custom Patches Mode
Use your own `patches.plist` file (for example, a custom AMD patch set you’ve modified):

```bash
python3 oc_amd_patch_auto.py --config /path/to/config.plist --patches /path/to/patches.plist --cores X
```

**Behavior:**
- Skips all downloading.
- Loads and applies patches from your provided plist.

---


###  Combining Options
You can combine the arguments for more control:

```bash

# Custom patches quietly
python3 oc_amd_patch_auto.py --config config.plist --patches mypatches.plist --quiet
```

---

### 🔹 Quiet Mode
Suppresses most log output (only errors are printed):

```bash
python3 oc_amd_patch_auto.py --config config.plist --beta --quiet
```

This mode is ideal for automation or silent batch runs.

---

##  Logging Examples

Standard output when running in normal mode:
```
[INFO] Loaded config from /path/to/config.plist
[INFO] Downloading release patches from https://raw.githubusercontent.com/AMD-OSX/AMD_Vanilla/master/patches.plist
[INFO] Successfully downloaded release patches.
[INFO] Removed 25 existing Kernel->Patch entries.
[INFO] Inserted 27 new patches.
[INFO] Set Kernel->Quirks->ProvideCurrentCpuInfo = True
[INFO] Config updated successfully: /path/to/config.plist

✅ Done!
 Patched config: /path/to/config.plist
 Source: release patches from AMD Vanilla repo
```

---
---

## Notes
- The script directly modifies your `config.plist` file — back it up manually if needed.
- Only OpenCore patches are supported (no Clover patches).
- The `--patches` flag overrides any downloading.

---

## 📜 License
This project is released under the [MIT License](LICENSE).

---

## ❤️ Credits
- **AMD Vanilla Team** – for maintaining the patch repositories.
- **OpenCore Project** – for the OpenCore bootloader.

---

## 🌟 Example Automation

Run automatically every time your config updates:
```bash
#!/bin/bash
python3 oc_amd_patch_auto.py --config ~/EFI/OC/config.plist --beta --quiet --cores 8
```
