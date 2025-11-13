
test = {'nmap': {'command_line': 'nmap -oX - -sn -T4 -n 10.0.3.0', 'scaninfo': {}, 'scanstats': {'timestr': 'Wed Nov 12 23:50:02 2025', 'elapsed': '0.44', 'uphosts': '0', 'downhosts': '1', 'totalhosts': '1'}}, 'scan': {}}
print(test['nmap']['scanstats']['uphosts'])
