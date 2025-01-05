import functools
import json

from pyncm.utils.crypto import EapiDecrypt, HexCompose

IGNORE_ARGS = {"e_r", "header"}
r = input("粘贴 EAPI params 参数>>>")
# Decrypting request
r = HexCompose(r)
r = EapiDecrypt(r).decode()
url, payload, _ = r.split("-36cd479b6b5-")
payload = json.loads(payload)
if isinstance(payload["header"], str):
    payload["header"] = json.loads(payload["header"])


def comp(s1, s2):
    if ("id" in s1.lower()) or s1 > s2:
        return -1
    if ("id" in s2.lower()) or s1 < s2:
        return 1
    return 0


print("Payload  ===============")
print(payload)
# Digesting info
print("== API Info ==============")
print(" URL:        ", url)
print("== Security ==============")
args = set(payload.keys())
args = args - IGNORE_ARGS
args = sorted(args, key=functools.cmp_to_key(comp))
print("== Parameters ============")
for arg in args:
    print(f"    {arg.ljust(16)}:      {payload[arg]}")


print("== Headers ===============")
for header in payload["header"]:
    print("    {}:      {}".format(header.ljust(16), payload["header"][header]))
