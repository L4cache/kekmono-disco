import pathlib
import bs4
import requests
import hashlib
import os
import re
import sys
arg_name = False
if len(sys.argv) > 1:
    arg_name = sys.argv[1]
def get_file_hash(file:str,blksize:int=4<<20):
    sha256_hash = hashlib.sha256()
    with open(file,"rb") as f:
        for byte_block in iter(lambda: f.read(blksize),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest().lower()

if arg_name:
    htm_fil = arg_name
else:
    htm_fil = input('htm(l) file name: ')
htm_fil = htm_fil.strip('"')
htm_fil_p = pathlib.Path(htm_fil).absolute()
htm_fil_f = htm_fil_p.parent / (htm_fil_p.name.split('.')[0]+'_files')
htm_fil_dl= htm_fil_f / 'originals'
htm_fil_dl.mkdir(exist_ok=True)

cookies = None
cookie_file = htm_fil_p.parent / 'cookies.txt'
if cookie_file.exists():
    from http.cookiejar import MozillaCookieJar
    cookies = MozillaCookieJar()
    loaded_cookies = MozillaCookieJar()
    loaded_cookies.load(cookie_file)

    for cookie in loaded_cookies:
        if cookie.domain.startswith('www.'):
            cookie.domain = cookie.domain[3:]
            cookie.domain_specified = True
            cookie.domain_initial_dot = True
        elif not cookie.domain.startswith('.'):
            cookie.domain = f'.{cookie.domain}'
            cookie.domain_specified = True
            cookie.domain_initial_dot = True
        cookies.set_cookie(cookie)

with open(htm_fil_p, encoding='utf-8') as fil:
    htm_string = fil.read()
    #soup = bs4.BeautifulSoup(htm_string)

prefix = ''.join(['https://','n','e','k','o','h','o','u','s','e','.','s','u','/data'])
rex = re.compile('/[0-9a-z]{2}/[0-9a-z]{2}/[0-9a-z]{64}\.[^?"]*')
data_paths = rex.findall(htm_string)
hrefs = [prefix+i for i in data_paths]
names = [os.path.splitext(i)[1] for i in data_paths]

hrefs_dd = []
names_dd = []
for n,i in enumerate(hrefs):
    if not i in hrefs_dd and '/data/' in i:
        hrefs_dd.append(i)
        names_dd.append(names[n])

#hrefs_dd = hrefs
#names_dd = names

tot = len(hrefs_dd)

target_fils = []
#fil_digits=len(str(tot))
for n,i in enumerate(hrefs_dd):
    fname = i.split('/')[-1]
    # sname, ext = fname.split('.')
    # oname = '.'.join([sname[:64], ext])
    # target_fils.append(htm_fil_f / oname)
    num = f'{n:09d}'
    unsafename = names_dd[n]
    safename = ''.join(i if i not in r'\/:*?"<>|' else '_' for i in unsafename)
    oname = '_'.join([num, safename])
    target_fils.append(htm_fil_dl / oname)

sus=requests.Session()
giveup=0
for n,i in enumerate(zip(hrefs_dd, target_fils)):
    srv_hash = i[0].split('/')[-1].split('.')[0]
    if os.path.exists(i[1]):
        loc_hash = get_file_hash(str(i[1]))
        if loc_hash == srv_hash:
            print(i[0], 'skipped', n+1, '/', tot)
            continue
    downloading=1
    while downloading:
        try:
            resp = sus.get(i[0],cookies=cookies)
            if resp.status_code != 200:
                raise ValueError(f'response not ok, code: {resp.status_code}')
            with open(i[1],'wb') as out:
                out.write(resp.content)
                downloading=0
                print(i[0], 'downloaded', n+1, '/', tot)
        except Exception as exc:
            print(f'{i[0]} Exception {exc}')
            quiz=input('retry? (1/0)')
            if quiz=='0':
                downloading=0
                giveup+=1
if not giveup:
    print('All files downloaded')
else:
    print(f'{giveup} files not downloaded')
sus.close()
if not arg_name:
    os.system('pause')