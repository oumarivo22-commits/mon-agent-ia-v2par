import os
from google_auth_oauthlib.flow import InstalledAppFlow

# This scope allows the app to manage your Blogger posts
SCOPES = ['https://www.googleapis.com/auth/blogger']
CLIENT_SECRETS_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

def run_authorization_flow():
    """
    Runs the OAuth 2.0 flow to get user authorization.
    This function will open a browser window for the user to grant permission.
    It saves the resulting token to 'token.json'.
    """
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"ERREUR: Le fichier '{CLIENT_SECRETS_FILE}' est introuvable.")
        print("Veuillez le télécharger depuis la Google Cloud Console et le placer dans le même dossier que ce script.")
        return

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    
    print("\n--- Processus d'autorisation Google ---")
    print("Ce script va maintenant ouvrir une page dans votre navigateur web.")
    print("Vous devrez vous connecter à votre compte Google et autoriser l'application 'Agent de blog' à accéder à votre blog.")
    print("Après avoir donné votre autorisation, vous serez peut-être redirigé vers une page 'localhost' qui affichera une erreur. C'est normal.")
    print("Copiez l'URL complète de cette page d'erreur et collez-la ici dans le terminal.\n")
    
    creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open(TOKEN_FILE, 'w') as token:
        token.write(creds.to_json())
    
    print(f"\nSUCCÈS ! L'autorisation a été enregistrée dans le fichier '{TOKEN_FILE}'.")
    print("Vous pouvez maintenant utiliser ce fichier pour votre agent sur Render.")

if __name__ == '__main__':
    run_authorization_flow()
