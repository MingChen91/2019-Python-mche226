import server_api
import helper_modules


list = server_api.list_users("mche226")
pubkey = helper_modules.get_pubkey(list,"mche226","gcoc113")

print(pubkey)