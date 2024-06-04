import pathlib
import bs4
import requests
import hashlib
import os
def get_file_hash(file:str):
    sha256_hash = hashlib.sha256()
    with open(file,"rb") as f:
        for byte_block in iter(lambda: f.read(4096),b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest().lower()

htm_fil = input('htm(l) file name: ')
htm_fil = htm_fil[1:] if htm_fil.startswith('"') else htm_fil
htm_fil = htm_fil[:-1] if htm_fil.endswith('"') else htm_fil
htm_fil_p = pathlib.Path(htm_fil).absolute()
htm_fil_f = htm_fil_p.parent / (htm_fil_p.name.split('.')[0]+'_files')

with open(htm_fil_p, encoding='utf-8') as fil:
    soup = bs4.BeautifulSoup(fil)
ass = soup.find_all('a')
hrefs = [i['href'] for i in ass]
hrefs = [i.split('?f=')[0] for i in hrefs]
hrefs_dd = []
for i in hrefs:
    if not i in hrefs_dd:
        hrefs_dd.append(i)
tot = len(hrefs_dd)

target_fils = []
for i in hrefs_dd:
    fname = i.split('/')[-1]
    sname, ext = fname.split('.')
    oname = '.'.join([sname[:-4], ext])
    target_fils.append(htm_fil_f / oname)

for n,i in enumerate(zip(hrefs_dd, target_fils)):
    srv_hash = i[0].split('/')[-1].split('.')[0]
    loc_hash = get_file_hash(str(i[1]))
    if loc_hash == srv_hash:
        print(i[0], 'skipped', n+1, '/', tot)
        continue
    resp = requests.get(i[0])
    with open(i[1],'wb') as out:
        out.write(resp.content)
    print(i[0], 'downloaded', n+1, '/', tot)
print('All files downloaded')
os.system('pause')