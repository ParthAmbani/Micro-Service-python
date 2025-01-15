import os, requests

def token(request):
    if not "Authorization" in request.headers:
        return None, ("missing authorization",401)
    
    token = request.headers["Authorization"]

    if not token:
        return None, ("missing authorization",401)
    
    responce = requests.post(
         f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
         headers={"Authorization": token},
    )

    if responce.status_code == 200:
        return responce.text, None
    else:
        return None, (responce.text, responce.status_code)
    