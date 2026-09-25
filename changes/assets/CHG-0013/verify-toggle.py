#!/usr/bin/env python3
import subprocess
import time


def remote(*args: str) -> str:
    return subprocess.check_output(["fcitx5-remote", *args], text=True).strip()


before = (remote(), remote("-n"))
subprocess.run(["fcitx5-remote", "-t"], check=True)
time.sleep(1)
after = (remote(), remote("-n"))
subprocess.run(["fcitx5-remote", "-t"], check=True)
time.sleep(1)
restored = (remote(), remote("-n"))
if before == after or before != restored:
    raise SystemExit(
        f"toggle cycle failed: before={before}, after={after}, restored={restored}"
    )
print("toggle-cycle=ok")
