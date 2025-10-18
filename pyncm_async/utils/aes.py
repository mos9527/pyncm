# From https://github.com/ricmoo/pyaes, MIT License
# All rights reserved by the original author.
# Modified for pyncm usage.

s_box = b"c|w{\xf2ko\xc50\x01g+\xfe\xd7\xabv\xca\x82\xc9}\xfaYG\xf0\xad\xd4\xa2\xaf\x9c\xa4r\xc0\xb7\xfd\x93&6?\xf7\xcc4\xa5\xe5\xf1q\xd81\x15\x04\xc7#\xc3\x18\x96\x05\x9a\x07\x12\x80\xe2\xeb'\xb2u\t\x83,\x1a\x1bnZ\xa0R;\xd6\xb3)\xe3/\x84S\xd1\x00\xed \xfc\xb1[j\xcb\xbe9JLX\xcf\xd0\xef\xaa\xfbCM3\x85E\xf9\x02\x7fP<\x9f\xa8Q\xa3@\x8f\x92\x9d8\xf5\xbc\xb6\xda!\x10\xff\xf3\xd2\xcd\x0c\x13\xec_\x97D\x17\xc4\xa7~=d]\x19s`\x81O\xdc\"*\x90\x88F\xee\xb8\x14\xde^\x0b\xdb\xe02:\nI\x06$\\\xc2\xd3\xacb\x91\x95\xe4y\xe7\xc87m\x8d\xd5N\xa9lV\xf4\xeaez\xae\x08\xbax%.\x1c\xa6\xb4\xc6\xe8\xddt\x1fK\xbd\x8b\x8ap>\xb5fH\x03\xf6\x0ea5W\xb9\x86\xc1\x1d\x9e\xe1\xf8\x98\x11i\xd9\x8e\x94\x9b\x1e\x87\xe9\xceU(\xdf\x8c\xa1\x89\r\xbf\xe6BhA\x99-\x0f\xb0T\xbb\x16"
inv_s_box = b"R\tj\xd506\xa58\xbf@\xa3\x9e\x81\xf3\xd7\xfb|\xe39\x82\x9b/\xff\x874\x8eCD\xc4\xde\xe9\xcbT{\x942\xa6\xc2#=\xeeL\x95\x0bB\xfa\xc3N\x08.\xa1f(\xd9$\xb2v[\xa2Im\x8b\xd1%r\xf8\xf6d\x86h\x98\x16\xd4\xa4\\\xcc]e\xb6\x92lpHP\xfd\xed\xb9\xda^\x15FW\xa7\x8d\x9d\x84\x90\xd8\xab\x00\x8c\xbc\xd3\n\xf7\xe4X\x05\xb8\xb3E\x06\xd0,\x1e\x8f\xca?\x0f\x02\xc1\xaf\xbd\x03\x01\x13\x8ak:\x91\x11AOg\xdc\xea\x97\xf2\xcf\xce\xf0\xb4\xe6s\x96\xact\"\xe7\xad5\x85\xe2\xf97\xe8\x1cu\xdfnG\xf1\x1aq\x1d)\xc5\x89o\xb7b\x0e\xaa\x18\xbe\x1b\xfcV>K\xc6\xd2y \x9a\xdb\xc0\xfex\xcdZ\xf4\x1f\xdd\xa83\x88\x07\xc71\xb1\x12\x10Y'\x80\xec_`Q\x7f\xa9\x19\xb5J\r-\xe5z\x9f\x93\xc9\x9c\xef\xa0\xe0;M\xae*\xf5\xb0\xc8\xeb\xbb<\x83S\x99a\x17+\x04~\xbaw\xd6&\xe1i\x14cU!\x0c}"
r_con = b"\x00\x01\x02\x04\x08\x10 @\x80\x1b6l\xd8\xabM\x9a/^\xbcc\xc6\x975j\xd4\xb3}\xfa\xef\xc5\x919"

def sub_bytes(s):
    for i in range(4):
        for j in range(4):
            s[i][j] = s_box[s[i][j]]


def inv_sub_bytes(s):
    for i in range(4):
        for j in range(4):
            s[i][j] = inv_s_box[s[i][j]]


def shift_rows(s):
    s[0][1], s[1][1], s[2][1], s[3][1] = s[1][1], s[2][1], s[3][1], s[0][1]
    s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
    s[0][3], s[1][3], s[2][3], s[3][3] = s[3][3], s[0][3], s[1][3], s[2][3]


def inv_shift_rows(s):
    s[0][1], s[1][1], s[2][1], s[3][1] = s[3][1], s[0][1], s[1][1], s[2][1]
    s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
    s[0][3], s[1][3], s[2][3], s[3][3] = s[1][3], s[2][3], s[3][3], s[0][3]


def add_round_key(s, k):
    for i in range(4):
        for j in range(4):
            s[i][j] ^= k[i][j]


xtime = lambda a: (((a << 1) ^ 0x1B) & 0xFF) if (a & 0x80) else (a << 1)


def mix_single_column(a):
    t = a[0] ^ a[1] ^ a[2] ^ a[3]
    u = a[0]
    a[0] ^= t ^ xtime(a[0] ^ a[1])
    a[1] ^= t ^ xtime(a[1] ^ a[2])
    a[2] ^= t ^ xtime(a[2] ^ a[3])
    a[3] ^= t ^ xtime(a[3] ^ u)


def mix_columns(s):
    for i in range(4):
        mix_single_column(s[i])


def inv_mix_columns(s):
    for i in range(4):
        u = xtime(xtime(s[i][0] ^ s[i][2]))
        v = xtime(xtime(s[i][1] ^ s[i][3]))
        s[i][0] ^= u
        s[i][1] ^= v
        s[i][2] ^= u
        s[i][3] ^= v
    mix_columns(s)

def bytes2matrix(text):
    """Converts a 16-byte array into a 4x4 matrix."""
    return [list(text[i : i + 4]) for i in range(0, len(text), 4)]


def matrix2bytes(matrix):
    """Converts a 4x4 matrix into a 16-byte array."""
    return bytes(sum(matrix, []))


def xor_bytes(a, b):
    """Returns a new byte array with the elements xor'ed."""
    return bytes(i ^ j for i, j in zip(a, b))


def inc_bytes(a):
    """Returns a new byte array with the value increment by 1"""
    out = list(a)
    for i in reversed(range(len(out))):
        if out[i] == 0xFF:
            out[i] = 0
        else:
            out[i] += 1
            break
    return bytes(out)


def split_blocks(message, block_size=16, require_padding=True):
    assert len(message) % block_size == 0 or not require_padding
    return [message[i : i + 16] for i in range(0, len(message), block_size)]


class AES:
    MODE_CBC = 0xFE
    MODE_ECB = 0xFF
    BLOCKSIZE = 128 >> 3  # blocksize in bytes, used for padding
    rounds_by_key_size = {16: 10, 24: 12, 32: 14}

    def __init__(self, master_key):
        assert len(master_key) in AES.rounds_by_key_size
        self.n_rounds = AES.rounds_by_key_size[len(master_key)]
        self._key_matrices = self._expand_key(master_key)

    def _expand_key(self, master_key):
        """Expands and returns a list of key matrices for the given master_key."""
        # Initialize round keys with raw key material.
        key_columns = bytes2matrix(master_key)
        iteration_size = len(master_key) // 4
        i = 1
        while len(key_columns) < (self.n_rounds + 1) * 4:
            # Copy previous word.
            word = list(key_columns[-1])
            # Perform schedule_core once every "row".
            if len(key_columns) % iteration_size == 0:
                # Circular shift.
                word.append(word.pop(0))
                # Map to S-BOX.
                word = [s_box[b] for b in word]
                # XOR with first byte of R-CON, since the others bytes of R-CON are 0.
                word[0] ^= r_con[i]
                i += 1
            elif len(master_key) == 32 and len(key_columns) % iteration_size == 4:
                # Run word through S-box in the fourth iteration when using a
                # 256-bit key.
                word = [s_box[b] for b in word]
            # XOR with equivalent word from previous iteration.
            word = xor_bytes(word, key_columns[-iteration_size])
            key_columns.append(word)
        # Group key words in 4x4 byte matrices.
        return [key_columns[4 * i : 4 * (i + 1)] for i in range(len(key_columns) // 4)]

    def encrypt_block(self, plaintext):
        """Encrypts a single block of 16 byte long plaintext."""
        assert len(plaintext) == 16

        plain_state = bytes2matrix(plaintext)

        add_round_key(plain_state, self._key_matrices[0])

        for i in range(1, self.n_rounds):
            sub_bytes(plain_state)
            shift_rows(plain_state)
            mix_columns(plain_state)
            add_round_key(plain_state, self._key_matrices[i])

        sub_bytes(plain_state)
        shift_rows(plain_state)
        add_round_key(plain_state, self._key_matrices[-1])

        return matrix2bytes(plain_state)

    def decrypt_block(self, ciphertext):
        """Decrypts a single block of 16 byte long ciphertext."""
        assert len(ciphertext) == 16

        cipher_state = bytes2matrix(ciphertext)

        add_round_key(cipher_state, self._key_matrices[-1])
        inv_shift_rows(cipher_state)
        inv_sub_bytes(cipher_state)

        for i in range(self.n_rounds - 1, 0, -1):
            add_round_key(cipher_state, self._key_matrices[i])
            inv_mix_columns(cipher_state)
            inv_shift_rows(cipher_state)
            inv_sub_bytes(cipher_state)

        add_round_key(cipher_state, self._key_matrices[0])

        return matrix2bytes(cipher_state)

    def encrypt_ecb_nopadding(self, plaintext):
        """
        Decrypts `plaintext` using ECB mode
        Assumes data is already padded.
        """
        return bytearray(
            b"".join(
                [
                    self.encrypt_block(plaintext_block)
                    for plaintext_block in split_blocks(plaintext)
                ]
            )
        )

    def decrypt_ecb_nopadding(self, ciphertext):
        """
        Decrypts `plaintext` using ECB mode
        Assumes data is already padded.
        """
        return bytearray(
            b"".join(
                [
                    self.decrypt_block(plaintext_block)
                    for plaintext_block in split_blocks(ciphertext)
                ]
            )
        )

    def encrypt_cbc_nopadding(self, plaintext, iv):
        """
        Encrypts `plaintext` using CBC mode and with the given initialization vector (iv).
        Assumes data is already padded.
        """
        assert len(iv) == 16

        blocks = []
        previous = iv
        for plaintext_block in split_blocks(plaintext):
            # CBC mode encrypt: encrypt(plaintext_block XOR previous)
            block = self.encrypt_block(xor_bytes(plaintext_block, previous))
            blocks.append(block)
            previous = block

        return bytearray(b"".join(blocks))

    def decrypt_cbc_nopadding(self, ciphertext, iv):
        """
        Decrypts `ciphertext` using CBC mode with the given initialization vector (iv).
        Assumes data is already padded.
        """
        assert len(iv) == 16
        blocks = []
        previous = iv
        for ciphertext_block in split_blocks(ciphertext):
            # CBC mode decrypt: previous XOR decrypt(ciphertext)
            blocks.append(xor_bytes(previous, self.decrypt_block(ciphertext_block)))
            previous = ciphertext_block
        return bytearray(b"".join(blocks))
