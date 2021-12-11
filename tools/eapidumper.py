import sys
sys.path.insert(0,'\\'.join(sys.path[0].split('\\')[:-1]))

import json,functools
from pyncm.utils.crypto import HexCompose,EapiDecrypt
IGNORE_ARGS = {'e_r','header'}
print('''========HELP========''')
print(' - This utility can help you create pyncm functions with ease')
print(' - For the parameter,one can easily fetched by using HTTP packet analyzers such as Fiddler')
print(' - The code generated may or may not work,extra work is still needed to get it up and running')
print(' - Copy and paste the request body (without `params=`) here:')
r = input('>>>')
# Decrypting request
r = HexCompose(r)
r = EapiDecrypt(r).decode()
url,payload,_ = r.split('-36cd479b6b5-')
payload = json.loads(payload)
print('Payload  ===============')
print(payload)
# Digesting info
print('API Info ================')
print(' URL:        ',url)
print('  Security ==============')
args = set(payload.keys())
args = args - IGNORE_ARGS
def comp(s1,s2):
    if ('id' in s1.lower()) or s1 > s2:return -1
    if ('id' in s2.lower()) or s1 < s2:return 1
    return 0
args = sorted(args,key=functools.cmp_to_key(comp))
print('  Parameters ============')
for arg in args:
    print('    %s:      %s' % (arg.ljust(16),payload[arg]))
