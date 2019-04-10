import requests, json

def eliminar():
	datos= {'clave': 'VuOvfxdGRuEvqOAcB9q7G65eTFmmO1fGqndwmLx5o5B5wKFJoU8aPS778aNx'}

	r = requests.post('https://127.0.0.1:443/main/eliminarExpirados/', verify=False,  data=datos)
	print(r.status_code)
	print(r.text)
	
	#r = requests.get('https://127.0.0.1:443/main/eliminarExpirados', verify=False )
	
	
def main():
	eliminar()
	return 0

if __name__ == '__main__':
	main()
