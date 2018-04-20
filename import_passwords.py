# Made by Eddie Bijnen  https://github.com/eddie4/Passbolt_import_script
# support the guys behind passbolt they do awesome work
import subprocess
import requests
import urllib
import time
import json
                                                            # Right click user manage your keys. Save pub key block mypupkey.gpg
                                                            # Import your key into gpg2 via gpg --import mypubkey.gpg
gpg_pub_email = "eddie@edworks.info"
public_key_id = "5a26bexxxxxxxxx-99c1-66bb57e9c1aa"         # you can get this from the database or requests to passbolt
CAKEPHP_cookie= "5t74gxxxxxxxxxxvrj7mu5mt82"                # you can get this from your browser
server = "passbolt.edworks.info"                            # your passbolt server
destination_group = "5ab4ef13-fxxxxxxxxxxxxxxx4a957e9c1aa"  # you can get this from the database or requests to passbolt
                                                            # useragent MUST MATCH the one you got the cookie from
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0"


def gpg_encrypt(password):
    file = open("password.txt", "w")
    file.write(password)
    file.close()

    subprocess.call(['gpg2','-a','--output','password.asc','--encrypt','--recipient',gpg_pub_email,'password.txt'])

    with open("password.asc") as f:
        data = f.read()
    f.close()

    subprocess.call(['rm','password.asc'])
    return urllib.quote_plus(data)


fname = "import.csv"
with open(fname) as f:
    data = f.readlines()

passwords=[]
for line in data:
    fields = line.split("\t")
    structured_fields = {
                'name': str(fields[0].replace("""\\""", "_")) + str(fields[1]),
                'username': fields[2],
                'password': fields[3],
                'gpg': gpg_encrypt(fields[3]),
                'uri': fields[4],
                'description': fields[5] + fields[6]
    }
    payload =   "Resource%5Bid%5D=&Resource%5Bname%5D="+structured_fields['name']+"&"+\
                "Resource%5Buri%5D="+structured_fields['uri']+"&" + \
                "Resource%5Busername%5D="+structured_fields['username']+"&" + \
                "Resource%5Bdescription%5D="+structured_fields['username']+"&" + \
                "Secret%5B0%5D%5Buser_id%5D="+public_key_id+"&" +\
                "Secret%5B0%5D%5Bdata%5D="+structured_fields['gpg']

    headers = {'User-Agent': useragent,
               'Accept': 'application/json, text/javascript, */*; q=0.01',
               'Accept-Language': 'nl,en-US;q=0.7,en;q=0.3',
               'Accept-Encoding': ' gzip, deflate',
               'Referer': 'https://'+server,
               'Content-Type': ' application/x-www-form-urlencoded; charset=UTF-8',
               'X-Requested-With': ' XMLHttpRequest',
               'Cookie': '_ga=GA1.2.572836833.1501236163; CAKEPHP='+CAKEPHP_cookie
               }

    r = requests.post("https://"+server+"/resources",  headers=headers, data=payload, timeout=5)
    response = json.loads(r.text)

    if r.status_code == 200:
        print "password created",structured_fields['name']
    else:
        print "PASSWORD CREAT FAILED: ", structured_fields['name']
        print structured_fields['uri']
        print r.text, "\n"
        print r.request.body, "\n"
        time.sleep(10)

    headers2 = {
        'Host': server,
        'User-Agent': useragent,
        'Accept': 'application/json',
        'Accept-Language': 'nl,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'content-type': 'application/json',
        'Content-Length': '131',
        'Cookie': '_ga=GA1.2.572836833.1501236163; CAKEPHP='+CAKEPHP_cookie
    }

    data = '{"Permissions": [{"Permission": {"aco": "Resource", "aro": "Group", "aro_foreign_key":"'+destination_group+'", "type": 1}}]}'


    r = requests.post("https://"+server+"/share/simulate/resource/"+response["body"]["Resource"]["id"]+".json?api-version=v1", headers=headers2, data=data, timeout=5)
    if r.status_code == 200:
        print "password share simulation OK"
    else:
        print "PASSWORD SHARE SIMULATION FAILED: ",structured_fields['name']
        print r.text, "\n"
        print r.request.body, "\n"
        time.sleep(10)



    payload = 'Permissions%5B0%5D%5BPermission%5D%5BisNew%5D=true&Permissions%5B0%5D%5BPermission%5D%5Baco%5D=Resource&Permissions%5B0%5D%5BPermission%5D%5Baco_foreign_key%5D='+response["body"]["Resource"]["id"]+'&Permissions%5B0%5D%5BPermission%5D%5Baro%5D=Group&Permissions%5B0%5D%5BPermission%5D%5Baro_foreign_key%5D='+destination_group+'&Permissions%5B0%5D%5BPermission%5D%5Btype%5D=15&Permissions%5B1%5D%5BPermission%5D%5Bid%5D='+response["body"]["UserResourcePermission"]["permission_id"]+'&Permissions%5B1%5D%5BPermission%5D%5Bdelete%5D=1'


    r = requests.put("https://"+server+"/share/Resource/"+response["body"]["Resource"]["id"]+".json", headers=headers, data=payload, timeout=5)
    if r.status_code == 200:
        print "password shared OK"
    else:
        print "PASSWORD SHARE FAILED: ",structured_fields['name']
        print r.text, "\n"
        print r.request.body, "\n"
        time.sleep(10)
    time.sleep(0.2)






