"""AES-128-CBC 解密 + 密钥派生（移植自 gan-cube-emu crypto.rs）"""
from Cryptodome.Cipher import AES


def derive_key_iv(mac: bytes, base_key: bytes, base_iv: bytes) -> tuple[bytes, bytes]:
    salt = bytes([mac[5], mac[4], mac[3], mac[2], mac[1], mac[0]])
    key = bytearray(base_key)
    iv = bytearray(base_iv)
    for i in range(6):
        key[i] = (key[i] + salt[i]) % 0xFF
        iv[i] = (iv[i] + salt[i]) % 0xFF
    return bytes(key), bytes(iv)


def decrypt_msg(data: bytes, key: bytes, iv: bytes) -> bytes:
    buf = bytearray(data)
    if len(buf) > 16:
        off = len(buf) - 16
        cipher = AES.new(key, AES.MODE_CBC, iv=iv)
        buf[off:] = cipher.decrypt(buf[off:off + 16])
    sz = min(16, len(buf))
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    buf[:sz] = cipher.decrypt(bytes(buf[:sz]))
    return bytes(buf)


# Gen2 base keys (from device_config/gen2.rs)
GEN2_BASE_KEY = bytes([
    0x01, 0x02, 0x42, 0x28, 0x31, 0x91, 0x16, 0x07,
    0x20, 0x05, 0x18, 0x54, 0x42, 0x11, 0x12, 0x53,
])
GEN2_BASE_IV = bytes([
    0x11, 0x03, 0x32, 0x28, 0x21, 0x01, 0x76, 0x27,
    0x20, 0x95, 0x78, 0x14, 0x32, 0x12, 0x02, 0x43,
])