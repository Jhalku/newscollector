import google_docs_helper

if __name__ == "__main__":
    print("Initiating Google OAuth flow...")
    creds = google_docs_helper.get_credentials()
    if creds and creds.valid:
        print("Login successful! token.json saved.")
    else:
        print("Login failed.")
