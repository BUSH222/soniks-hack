import requests

server_url = int(input("Soniks server URL: "))
station_id = int(input("Soniks station id: "))
API_KEY = int(input("Soniks API KEY: "))
station_address = int(input("Station ip address + port: "))

d = requests.get(f"http://{server_url}/stations/{station_id}/register_sdr?address={station_address}&key={API_KEY}")

print(d.status_code)
print(d.text)
