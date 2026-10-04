"""Store an OpenAI key without security CLI's 128-character prompt truncation."""

import ctypes
import getpass


def store_password(service: str, account: str, password: str) -> None:
    security = ctypes.CDLL("/System/Library/Frameworks/Security.framework/Security")
    core = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
    find = security.SecKeychainFindGenericPassword
    find.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_char_p,
        ctypes.c_uint32,
        ctypes.c_char_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    find.restype = ctypes.c_int32
    add = security.SecKeychainAddGenericPassword
    add.argtypes = [
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_char_p,
        ctypes.c_uint32,
        ctypes.c_char_p,
        ctypes.c_uint32,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    add.restype = ctypes.c_int32
    modify = security.SecKeychainItemModifyAttributesAndData
    modify.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
    modify.restype = ctypes.c_int32
    core.CFRelease.argtypes = [ctypes.c_void_p]
    svc, acct, secret = service.encode(), account.encode(), password.encode()
    item = ctypes.c_void_p()
    status = find(None, len(svc), svc, len(acct), acct, None, None, ctypes.byref(item))
    if status == 0:
        try:
            status = modify(item, None, len(secret), secret)
        finally:
            core.CFRelease(item)
    elif status == -25300:
        status = add(None, len(svc), svc, len(acct), acct, len(secret), secret, None)
    if status:
        raise RuntimeError(f"Keychain operation failed: OSStatus {status}")


if __name__ == "__main__":
    key = getpass.getpass("OpenAI API key (hidden): ")
    if not key.startswith("sk-") or any(c.isspace() for c in key):
        raise SystemExit("Expected an API key without whitespace; nothing stored.")
    store_password("aletheia-openai-api-key", getpass.getuser(), key)
    print("Stored full credential in Keychain; no key printed.")
