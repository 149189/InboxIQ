import os, base64, json, datetime, requests
from celery import shared_task
from .models import Draft
from auth_app.models import User

@shared_task
def save_draft_to_gmail(draft_id):
    try:
        d = Draft.objects.get(id=draft_id)
        user = d.user
        if not user.google_refresh_token:
            return {'status':'no_google_token'}
        # refresh token
        token_url = 'https://oauth2.googleapis.com/token'
        data = {
            'client_id': os.getenv('GOOGLE_CLIENT_ID'),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET'),
            'refresh_token': user.google_refresh_token,
            'grant_type': 'refresh_token'
        }
        r = requests.post(token_url, data=data)
        if r.status_code != 200:
            return {'status':'token_refresh_failed','code':r.status_code,'text':r.text}
        access = r.json().get('access_token')
        # build raw RFC 2822 message
        raw = (f"From: me\nTo: {', '.join(d.to_emails)}\nSubject: {d.subject}\nContent-Type: text/html; charset=utf-8\n\n{d.body_html}")
        raw_b64 = base64.urlsafe_b64encode(raw.encode('utf-8')).decode('utf-8')
        # call Gmail API to create draft
        url = 'https://gmail.googleapis.com/gmail/v1/users/me/drafts'
        headers = {'Authorization': f'Bearer {access}', 'Content-Type':'application/json'}
        payload = {'message': {'raw': raw_b64}}
        r2 = requests.post(url, headers=headers, json=payload)
        if r2.status_code in (200,201):
            d.external_draft_id = r2.json().get('id')
            d.save()
            return {'status':'ok','id':d.external_draft_id}
        else:
            return {'status':'failed','code':r2.status_code,'text':r2.text}
    except Exception as e:
        return {'status':'error','error':str(e)}
