import requests

t=requests.post('http://localhost:8000/api/v1/auth/connexion',json={'nom_utilisateur':'testuser','mot_de_passe':'testpassword123'}).json()['access_token']
h={'Authorization':f'Bearer {t}'}
ps=requests.get('http://localhost:8000/api/v1/teams/2/available-players',headers=h,params={'limit':100}).json()['players']
cheap=[p for p in ps if p['is_affordable']]
cheap.sort(key=lambda x:x['player']['fantasy_cost'])
print(f'\n✅ Joueurs < $2.4M: {len(cheap)}\n')
for p in cheap[:10]:
    if p['player']['fantasy_cost'] <= 2400000:
        print(f"  ID {p['player']['id']}: {p['player']['first_name']} {p['player']['last_name']} ({p['player']['position']}) - ${p['player']['fantasy_cost']/1_000_000:.1f}M")

if cheap:
    selected = cheap[0]['player']
    print(f"\n🎯 Ajout de {selected['first_name']} {selected['last_name']} en UTIL...")
    result = requests.post('http://localhost:8000/api/v1/teams/2/roster', headers=h, json={'player_id': selected['id'], 'position_slot': 'UTIL'})
    
    if result.status_code == 201:
        data = result.json()
        print(f"\n✅ ROSTER COMPLET ! (6/6)")
        print(f"\n📢 MESSAGE DU SERVEUR :")
        for line in data['message'].split('\\n'):
            print(f"   {line}")
    else:
        print(f"\n❌ Erreur : {result.json().get('detail')}")
