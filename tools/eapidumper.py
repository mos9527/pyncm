import pyncm,json,functools
SEC_ARGS = {'checkToken'}
SEC_RESOLUTION = {'checkToken':'Crypto.checkToken()'}
IGNORE_ARGS = {'e_r','header'}
print('''========HELP========''')
print(' - This utility can help you create pyncm functions with ease')
print(' - For the parameter,one can easily fetched by using HTTP packet analyzers such as Fiddler')
print(' - The code generated may or may not work,extra work is still needed to get it up and running')
print(' - Copy and paste the request body (without `params=`) here:')
r = input('>>>')
# Decrypting request
r = pyncm.Crypto.HexCompose(r)
r = pyncm.Crypto.EapiDecrypt(r).decode()
url,payload,_ = r.split('-36cd479b6b5-')
payload = json.loads(payload)
print('Payload  ===============')
print(payload)
# Digesting info
print('API Info ================')
print(' URL:        ',url)
print('  Security ==============')
for sec_arg in SEC_ARGS:
    print('    %s:      %s' % (sec_arg.ljust(16),sec_arg in payload))
args = set(payload.keys()) - SEC_ARGS
args = args - IGNORE_ARGS
def comp(s1,s2):
    if ('id' in s1.lower()) or s1 > s2:return -1
    if ('id' in s2.lower()) or s1 < s2:return 1
    return 0
args = sorted(args,key=functools.cmp_to_key(comp))
print('  Parameters ============')
for arg in args:
    print('    %s:      %s' % (arg.ljust(16),payload[arg]))
# Generating code
print('  Pesudo-Code ===========')
code = '''@EapiCryptoRequest
def %s(%s):
    return '%s',%s
''' % (
    ''.join(s.capitalize() for s in url.split('/')[2:]),
    ','.join(args),
    url.replace('/api/','/eapi/'),
    '{%s}' % ','.join(['"%s":str(%s)' % (s,s) for s in args] + ['"%s":%s' % (s,SEC_RESOLUTION[s]) for s in SEC_ARGS])
)
print(code)