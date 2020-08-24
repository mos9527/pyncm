import base64,os,re

regex = re.compile(r'(?<=a\.c\(\")[a-zA-Z0-9+\/=]*(?=\"\))')
magic = b"Encrypt"
decomp_path = 'D:\\ncm\\classes-dex2jar.jar.src\\'

def perByteXOR(buffer,magic):
    for i in range(0, len(buffer)):
        # in-place xor，where the xor char is the `i modulo magic-len`th char of our magic
        xor_char = magic[i % len(magic)]
        buffer[i] = buffer[i] ^ xor_char

def encode(p):
    buffer = list(p.encode())
    perByteXOR(buffer,magic)
    return base64.b64encode(bytearray(buffer))

def decode(p):
    buffer = list(base64.b64decode(p))
    perByteXOR(buffer,magic)
    return bytearray(buffer).decode()

def traverse(p,d=0):
    # p -> path,d -> depth
    for sp in os.listdir(p):
        fp = os.path.join(p,sp)
        # fp -> fullpath
        if os.path.isdir(fp):
            # continue to travese direcories
            traverse(fp,d+1)
        else:
            # dealing with our coods,line by line
            lines = open(fp,'r',encoding='utf-8').readlines()
            for rp in range(0,len(lines)):
                line = lines[rp]
                find = regex.findall(line)
                if find:
                  for f in find:
                    line = line.replace(f,decode(f))
                  lines[rp] = line  
            open(fp,'w',encoding='utf-8').writelines(lines)              
traverse(decomp_path)
while True:
  print(
    encode(input('>>>'))
  )