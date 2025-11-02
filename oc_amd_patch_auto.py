#!/usr/bin/env python3
import argparse, os, sys, plistlib, binascii, urllib.request

RELEASE_URL = "https://raw.githubusercontent.com/AMD-OSX/AMD_Vanilla/master/patches.plist"
BETA_URL = "https://raw.githubusercontent.com/AMD-OSX/AMD_Vanilla/refs/heads/beta/patches.plist"

def log(msg, quiet=False, level="INFO"):
    if quiet:
        return
    print(f"[{level}] {msg}")


def load_plist(path):
    with open(path, "rb") as f:
        return plistlib.load(f)


def save_plist(obj, path):
    with open(path, "wb") as f:
        plistlib.dump(obj, f, fmt=plistlib.FMT_XML, sort_keys=True)


def ensure_path(dct, path, final_type):
    cur = dct
    for i, key in enumerate(path):
        if key not in cur:
            cur[key] = {} if i < len(path) - 1 else (final_type() if callable(final_type) else final_type)
        cur = cur[key]
    return dct


def extract_data(value):
    if hasattr(plistlib, "Data") and isinstance(value, plistlib.Data):
        return value.data
    return value


def wrap_data(value):
    if hasattr(plistlib, "Data"):
        return plistlib.Data(value)
    return value


def download_patches(url):
    with urllib.request.urlopen(url) as r:
        data = r.read()
    return plistlib.loads(data)


def set_cpu_cores_in_patch(patch_dict, cores, quiet=False):
    comment = str(patch_dict.get("Comment", "")).lower()
    if "force cpuid_cores_per_package" not in comment:
        return False
    repl = patch_dict.get("Replace")
    if repl is None:
        return False
    repl_bytes = extract_data(repl)
    if not isinstance(repl_bytes, (bytes, bytearray)):
        return False
    hex_str = binascii.hexlify(repl_bytes).decode("utf-8")
    c = max(1, min(int(cores), 255))
    new_hex = hex_str[:2] + f"{c:02x}" + hex_str[4:]
    new_bytes = binascii.unhexlify(new_hex.encode("utf-8"))
    patch_dict["Replace"] = wrap_data(new_bytes)
    log(f"Adjusted cpuid_cores_per_package patch to {cores} cores.", quiet)
    return True


def wipe_kernel_patches(config, quiet=False):
    ensure_path(config, ["Kernel", "Patch"], list)
    count = len(config["Kernel"]["Patch"])
    config["Kernel"]["Patch"] = []
    log(f"Removed {count} existing Kernel->Patch entries.", quiet)
    return config


def insert_oc_patches(config, oc_patches, cores=None, quiet=False):
    if "Kernel" not in oc_patches or "Patch" not in oc_patches["Kernel"]:
        raise RuntimeError("Provided patches.plist does not contain Kernel->Patch entries.")

    ensure_path(config, ["Kernel", "Patch"], list)
    ensure_path(config, ["Kernel", "Quirks"], dict)

    new_patches = []
    for p in oc_patches["Kernel"]["Patch"]:
        if cores is not None:
            try:
                set_cpu_cores_in_patch(p, cores, quiet)
            except Exception:
                pass
        new_patches.append(p)

    config["Kernel"]["Patch"] = new_patches
    config["Kernel"]["Quirks"]["ProvideCurrentCpuInfo"] = True

    log(f"Inserted {len(new_patches)} new patches.", quiet)
    log("Set Kernel->Quirks->ProvideCurrentCpuInfo = True", quiet)
    return config


def main():
    ap = argparse.ArgumentParser(description="Apply AMD Vanilla OpenCore patches automatically with logging and modes.")
    ap.add_argument("--config", required=True, help="Path to your OpenCore config.plist")
    ap.add_argument("--patches", help="Path to a custom local patches.plist file")
    ap.add_argument("--beta", action="store_true", help="Download and apply beta patches instead of release")
    ap.add_argument("--cores", type=int, default=None, help="CPU core count (optional)")
    ap.add_argument("--quiet", action="store_true", help="Suppress logging output (quiet mode)")
    args = ap.parse_args()

    quiet = args.quiet
    cfg_path = os.path.abspath(args.config)

    if not os.path.isfile(cfg_path):
        print(f"[ERROR] Config not found: {cfg_path}")
        sys.exit(1)

    try:
        config = load_plist(cfg_path)
        log(f"Loaded config from {cfg_path}", quiet)
    except Exception as e:
        print(f"[ERROR] Failed to load target plist: {e}")
        sys.exit(1)

    if args.patches:
        patch_source = os.path.abspath(args.patches)
        if not os.path.isfile(patch_source):
            print(f"[ERROR] Patches file not found: {patch_source}")
            sys.exit(1)
        try:
            oc_patches = load_plist(patch_source)
            log(f"Loaded custom patches from: {patch_source}", quiet)
        except Exception as e:
            print(f"[ERROR] Failed to load patches plist: {e}")
            sys.exit(1)

    else:
        url = BETA_URL if args.beta else RELEASE_URL
        mode = "beta" if args.beta else "release"
        try:
            log(f"Downloading {mode} patches from {url}", quiet)
            oc_patches = download_patches(url)
            log(f"Successfully downloaded {mode} patches.", quiet)
        except Exception as e:
            print(f"[ERROR] Failed to download {mode} patches: {e}")
            sys.exit(1)

    wipe_kernel_patches(config, quiet)
    insert_oc_patches(config, oc_patches, cores=args.cores, quiet=quiet)

    try:
        save_plist(config, cfg_path)
        log(f"Config updated successfully: {cfg_path}", quiet)
    except Exception as e:
        print(f"[ERROR] Failed to save config: {e}")
        sys.exit(1)

    if not quiet:
        print("\n Done!")
        print(f" Patched config: {cfg_path}")
        if args.patches:
            print(f" Source: {patch_source}")
        else:
            print(f" Source: {'beta' if args.beta else 'release'} patches from AMD Vanilla repo")
        if args.cores is not None:
            print(f" CPU cores set: {args.cores}")


if __name__ == "__main__":
    main()
