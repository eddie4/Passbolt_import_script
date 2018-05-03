# Made by Eddie Bijnen  https://github.com/eddie4/Passbolt_import_script
# support the guys behind passbolt they do awesome work

import requests
import urllib

default_rol_id = "d1acbfc1-xxxxx-3e25-xxxx-7ab1eb0332dc"      # you can get this from the database or requests to passbolt
CAKEPHP_cookie = "2eki5kxxxxxxxxx0tr2ghcejcn7"                # you can get this from the browser
                                                              # useragent MUST MATCH the one you got the cookie from
user_agent     = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"
server         = "passbolt.edworks.info"


fname = "users.csv"
with open(fname) as f:
    data = f.readlines()

passwords=[]
for line in data:
    fields = line.split("\t")
    name_subfields = fields[0].split(" ")
    lastname = ""
    for name in name_subfields[1:]:
        lastname += name + " "

    lastname = lastname[0:-1]
    structured_fields = {

                'firstname':name_subfields[0],
                'lastname': lastname,
                'email': fields[2]
    }
    print structured_fields

    payload =   "User%5Bactive%5D=1&" \
                "User%5Brole_id%5D="+default_rol_id+"&" \
                "User%5Busername%5D="+urllib.quote_plus(structured_fields['email'])+"&" \
                "Profile%5Bfirst_name%5D="+structured_fields['firstname']+"&" \
                "Profile%5Blast_name%5D="+structured_fields['lastname']

    headers = {'Host': server,
               'User-Agent': user_agent,
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept-Language': 'nl,en-US;q=0.7,en;q=0.3',
               'Accept-Encoding': 'gzip, deflate',
               'Referer': 'https://'+server+'/',
               'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
               'X-Requested-With': 'XMLHttpRequest',
               'Cookie': '_ga=GA1.2.572836833.1501236163; CAKEPHP='+CAKEPHP_cookie}

    r = requests.post("https://"+server+"/users",  headers=headers, data=payload)

    if r.status_code == 200:
        print "user created"

    else:
        print "FAILED",structured_fields
        print r.text
        print r.request.body
        print r.request.headers
        time.sleep(10)
