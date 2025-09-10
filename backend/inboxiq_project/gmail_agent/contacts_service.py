# gmail_agent/contacts_service.py
import re
from difflib import SequenceMatcher
from django.db import transaction
from django.conf import settings
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from .models import ContactCache  # adjust import if models in different path

# If you use googleapiclient, ensure it's installed and OAuth token scopes include contacts
# pip install google-api-python-client google-auth

class GoogleContactsService:
    def __init__(self, access_token, refresh_token=None):
        self.access_token = access_token
        self.refresh_token = refresh_token

    def _build_people_service(self):
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            creds = Credentials(token=self.access_token,
                refresh_token=self.refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=settings.GOOGLE_OAUTH_CLIENT_ID,
                client_secret=settings.GOOGLE_OAUTH_CLIENT_SECRET)
            service = build('people', 'v1', credentials=creds, cache_discovery=False)
            return service
        except Exception as e:
            print(f"[CONTACTS] Failed to build People API client: {e}")
            return None

    def _is_email(self, term: str) -> bool:
        return bool(re.match(r"[^@]+@[^@]+\.[^@]+", term))

    def _similarity(self, a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def fetch_all_contacts_from_api(self, page_size=2000):
        """Fetch connections from People API. Returns list of dicts."""
        service = self._build_people_service()
        contacts = []
        if not service:
            print("[CONTACTS] People API service not available")
            return contacts

        try:
            req = service.people().connections().list(
                resourceName='people/me',
                personFields='names,emailAddresses,photos',
                pageSize=page_size
            )
            while req:
                res = req.execute()
                connections = res.get('connections', [])
                for p in connections:
                    names = p.get('names', [])
                    emails = p.get('emailAddresses', [])
                    photos = p.get('photos', [])
                    display_name = names[0].get('displayName') if names else ''
                    primary_email = emails[0].get('value') if emails else ''
                    photo_url = photos[0].get('url') if photos else ''
                    contacts.append({
                        'display_name': display_name,
                        'primary_email': primary_email,
                        'photo_url': photo_url
                    })
                # Use people().connections().list_next if available
                try:
                    req = service.people().connections().list_next(req, res)
                except Exception:
                    req = None
        except Exception as e:
            print(f"[CONTACTS] Error fetching contacts via People API: {e}")

        return contacts

    def _filter_contacts(self, contacts, search_terms, threshold=0.60):
        """Filter and rank contacts given search terms. Returns sorted list."""
        results = []
        seen = set()
        for c in contacts:
            name = (c.get('display_name') or '').strip()
            email = (c.get('primary_email') or '').strip()
            best_score = 0.0
            for term in search_terms:
                term = term.strip()
                if not term:
                    continue
                # exact email match highest priority
                if email and term.lower() == email.lower():
                    best_score = 1.0
                    break
                # substring match
                if term.lower() in name.lower() or term.lower() in email.lower():
                    best_score = max(best_score, 0.9)
                else:
                    name_sim = self._similarity(name, term) if name else 0.0
                    email_sim = self._similarity(email, term) if email else 0.0
                    best_score = max(best_score, name_sim, email_sim)
            if best_score >= threshold:
                key = (email.lower() if email else name.lower())
                if key not in seen:
                    seen.add(key)
                    results.append((best_score, c))
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results]

    def _search_contactcache_db(self, user, search_terms):
        """Search ContactCache DB for quick lookup (if you maintain a cache)."""
        try:
            qs = ContactCache.objects.filter(user=user)
            found = []
            for c in qs:
                cn = {'display_name': c.display_name or '', 'primary_email': c.primary_email or '', 'photo_url': c.photo_url or ''}
                if any((t.lower() in (cn['display_name'] or '').lower()) or (t.lower() in (cn['primary_email'] or '').lower()) for t in search_terms):
                    found.append(cn)
            return found
        except Exception as e:
            print(f"[CONTACTS] DB cache search error: {e}")
            return []

    def _maybe_update_cache(self, user, contacts):
        """Optional: update ContactCache entries (best-effort)."""
        try:
            with transaction.atomic():
                for c in contacts:
                    if not c.get('primary_email'):
                        continue
                    ContactCache.objects.update_or_create(
                        user=user, primary_email=c['primary_email'],
                        defaults={'display_name': c.get('display_name', ''), 'photo_url': c.get('photo_url', '')}
                    )
        except Exception as e:
            print(f"[CONTACTS] Failed to update cache: {e}")

    def search_contacts(self, user, search_terms):
        """
        Main entry point:
        - If any term looks like an email, do quick exact-match cache lookup.
        - Else fetch People API contacts and filter locally.
        - Fallback to DB cache search.
        Returns list of dicts: [{'display_name','primary_email','photo_url'}, ...]
        """
        if not search_terms:
            print("[CONTACTS] No search_terms provided")
            return []

        search_terms = [str(t).strip() for t in search_terms if t and str(t).strip()]
        print(f"[CONTACTS] search_contacts called with terms={search_terms!r}")

        # If any term is an explicit email, try exact-match cache first
        for term in search_terms:
            if self._is_email(term):
                try:
                    cached = ContactCache.objects.filter(user=user, primary_email__iexact=term)
                    if cached.exists():
                        res = [{
                            'display_name': c.display_name,
                            'primary_email': c.primary_email,
                            'photo_url': c.photo_url
                        } for c in cached]
                        print(f"[CONTACTS] Found {len(res)} matches in ContactCache for email {term}")
                        return res
                except Exception as e:
                    print(f"[CONTACTS] ContactCache query failed: {e}")

        # Try People API
        contacts = self.fetch_all_contacts_from_api()
        print(f"[CONTACTS] fetch_all_contacts_from_api returned {len(contacts)} contacts")
        if contacts:
            try:
                self._maybe_update_cache(user, contacts)
            except Exception:
                pass
            filtered = self._filter_contacts(contacts, search_terms)
            print(f"[CONTACTS] Filtered down to {len(filtered)} matches")
            return filtered

        # Fallback: search local cache DB
        cached_found = self._search_contactcache_db(user, search_terms)
        print(f"[CONTACTS] DB cache fallback found {len(cached_found)} matches")
        return cached_found
