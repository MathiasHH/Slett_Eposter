import imaplib
import email
from email.header import decode_header

# Funksjon for å rydde opp i e-poster basert på sletting og hviteliste nøkkelord
def delete_emails_by_keywords(email_user, email_pass, delete_keywords, whitelist_keywords):
    # Connect to the IMAP server
    imap_server = "imap.gmail.com"  # Change this if you're using a different provider
    mail = imaplib.IMAP4_SSL(imap_server)
    
    try:
        # Logg på e-postkontoen
        mail.login(email_user, email_pass)
        print("Successfully logged in!")

        # Velg postkassen du vil slette e-poster fra (innboks som standard)
        mail.select("inbox")

        # Iterer gjennom alle de angitte slettenøkkelordene for å søke og slette e-poster
        for delete_keyword in delete_keywords:
            # Søk etter e-poster som inneholder nøkkelordet slette i emnet eller brødteksten
            status, messages = mail.search(None, f'(BODY "{delete_keyword}")')
            
           # Få listen over e-post-IDer som samsvarer med søket
            email_ids = messages[0].split()
     
            if not email_ids:
                print(f"Fant ingen e-poster for nøkkelordet: {delete_keyword}") #Nøkkelord = keyword
                continue

            print(f"Fnat {len(email_ids)} emails for nøkkelordet: {delete_keyword}")

            # Iterer gjennom hver e-post du finner
            for email_id in email_ids:
               # Hent e-posten med ID
                status, msg_data = mail.fetch(email_id, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8")
                        body = self.get_email_body(msg)

                        # Sjekk om noen hvitelistenøkkelord finnes i emnet eller brødteksten
                        if any(whitelist_keyword.lower() in (subject.lower() + body.lower()) for whitelist_keyword in whitelist_keywords):
                            print(f"Skipping email with subject: {subject} (matched a whitelist keyword)")
                            continue

                        # Merk e-posten for sletting hvis den ikke samsvarer med noen hvitelistesøkeord
                        print(f"Deleting email with subject: {subject}")
                        mail.store(email_id, '+FLAGS', '\\Deleted')

        # Fjern (slett permanent) e-postene som er merket for sletting
        mail.expunge()
        print("Emails sletta suksesfullt!")

    except Exception as e:
        print(f"Ein feil skjedde: {e}")

    finally:
        # Logg ut fra e-postkontoen
        mail.logout()

# Funksjon for å få e-postteksten (inne i EmailReader-klassen eller frittstående)
def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()

# Eksempel på bruk
if __name__ == "__main__":
    # Innloggingsdetaljer (erstatt med dine egne)
    email_user = "youremail@example.com"
    email_pass = "yourpassword"

    # Nøkkelord å se etter for å slette
    delete_keywords = ["unsubscribe", "promotion", "sale", "spam"]  # Example delete keywords

    # Nøkkelord som forhindrer at e-posten slettes
    whitelist_keywords = ["invoice", "receipt", "order", "important"]  # Example whitelist keywords

    # Ring funksjonen for å slette e-poster basert på nøkkelord og hviteliste
    delete_emails_by_keywords(email_user, email_pass, delete_keywords, whitelist_keywords)
