# backend/inboxiq_project/gmail_agent/contacts_service.py
import requests
from typing import List, Dict, Optional
from django.conf import settings
from .models import ContactCache
import json


class GoogleContactsService:
    """Service for interacting with Google Contacts API"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://people.googleapis.com/v1"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def search_contacts(self, user, search_terms: List[str]) -> List[Dict]:
        """
        Search for contacts using multiple search terms
        Returns list of contact matches with confidence scores
        """
        all_matches = []
        
        for term in search_terms:
            matches = self._search_single_term(user, term)
            for match in matches:
                # Add search term that found this contact
                match['found_by_term'] = term
                all_matches.append(match)
        
        # Remove duplicates and rank by relevance
        unique_matches = self._deduplicate_contacts(all_matches)
        ranked_matches = self._rank_contacts(unique_matches, search_terms)
        
        return ranked_matches[:5]  # Return top 5 matches
    
    def _search_single_term(self, user, search_term: str) -> List[Dict]:
        """Search contacts for a single term"""
        try:
            # First try to get from cache
            cached_contacts = ContactCache.objects.filter(
                user=user,
                name__icontains=search_term
            )
            
            if cached_contacts.exists():
                return [self._format_cached_contact(contact) for contact in cached_contacts]
            
            # If not in cache, search via API
            url = f"{self.base_url}/people:searchContacts"
            params = {
                'query': search_term,
                'readMask': 'names,emailAddresses,phoneNumbers,photos'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                contacts = []
                
                for result in data.get('results', []):
                    person = result.get('person', {})
                    contact_info = self._extract_contact_info(person)
                    if contact_info:
                        # Cache the contact
                        self._cache_contact(user, person, contact_info)
                        contacts.append(contact_info)
                
                return contacts
            else:
                print(f"Error searching contacts: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"Error in contact search: {e}")
            return []
    
    def _extract_contact_info(self, person: Dict) -> Optional[Dict]:
        """Extract relevant information from Google People API person object"""
        try:
            # Get name
            names = person.get('names', [])
            if not names:
                return None
            
            display_name = names[0].get('displayName', '')
            given_name = names[0].get('givenName', '')
            family_name = names[0].get('familyName', '')
            
            # Get email addresses
            email_addresses = person.get('emailAddresses', [])
            primary_email = None
            all_emails = []
            
            for email in email_addresses:
                email_addr = email.get('value', '')
                if email_addr:
                    all_emails.append(email_addr)
                    if not primary_email or email.get('metadata', {}).get('primary', False):
                        primary_email = email_addr
            
            if not primary_email and all_emails:
                primary_email = all_emails[0]
            
            if not primary_email:
                return None
            
            # Get phone numbers
            phone_numbers = person.get('phoneNumbers', [])
            primary_phone = phone_numbers[0].get('value', '') if phone_numbers else ''
            
            # Get photo
            photos = person.get('photos', [])
            photo_url = photos[0].get('url', '') if photos else ''
            
            return {
                'resource_name': person.get('resourceName', ''),
                'display_name': display_name,
                'given_name': given_name,
                'family_name': family_name,
                'primary_email': primary_email,
                'all_emails': all_emails,
                'primary_phone': primary_phone,
                'photo_url': photo_url,
                'confidence': 1.0,  # Will be adjusted by ranking algorithm
                'raw_data': person
            }
            
        except Exception as e:
            print(f"Error extracting contact info: {e}")
            return None
    
    def _cache_contact(self, user, person_data: Dict, contact_info: Dict):
        """Cache contact information for faster future searches"""
        try:
            resource_name = person_data.get('resourceName', '')
            contact_id = resource_name.split('/')[-1] if resource_name else ''
            
            if not contact_id:
                return
            
            ContactCache.objects.update_or_create(
                user=user,
                contact_id=contact_id,
                defaults={
                    'name': contact_info['display_name'],
                    'email': contact_info['primary_email'],
                    'phone': contact_info['primary_phone'],
                    'contact_data': person_data
                }
            )
        except Exception as e:
            print(f"Error caching contact: {e}")
    
    def _format_cached_contact(self, cached_contact: ContactCache) -> Dict:
        """Format cached contact for consistent return format"""
        return {
            'resource_name': f"people/{cached_contact.contact_id}",
            'display_name': cached_contact.name,
            'given_name': cached_contact.contact_data.get('names', [{}])[0].get('givenName', ''),
            'family_name': cached_contact.contact_data.get('names', [{}])[0].get('familyName', ''),
            'primary_email': cached_contact.email,
            'all_emails': [cached_contact.email],
            'primary_phone': cached_contact.phone,
            'photo_url': '',
            'confidence': 1.0,
            'raw_data': cached_contact.contact_data,
            'from_cache': True
        }
    
    def _deduplicate_contacts(self, contacts: List[Dict]) -> List[Dict]:
        """Remove duplicate contacts based on email address"""
        seen_emails = set()
        unique_contacts = []
        
        for contact in contacts:
            email = contact['primary_email'].lower()
            if email not in seen_emails:
                seen_emails.add(email)
                unique_contacts.append(contact)
        
        return unique_contacts
    
    def _rank_contacts(self, contacts: List[Dict], search_terms: List[str]) -> List[Dict]:
        """Rank contacts by relevance to search terms"""
        for contact in contacts:
            score = 0
            name_lower = contact['display_name'].lower()
            
            # Higher score for exact matches
            for i, term in enumerate(search_terms):
                term_lower = term.lower()
                
                # Exact name match gets highest score
                if term_lower == name_lower:
                    score += 100 - (i * 10)  # Earlier terms get higher score
                # Name contains term
                elif term_lower in name_lower:
                    score += 50 - (i * 5)
                # Term contains name (for partial matches)
                elif name_lower in term_lower:
                    score += 30 - (i * 3)
                
                # Check individual name parts
                given_name = contact.get('given_name', '').lower()
                family_name = contact.get('family_name', '').lower()
                
                if term_lower == given_name or term_lower == family_name:
                    score += 40 - (i * 4)
            
            contact['confidence'] = min(score / 100.0, 1.0)  # Normalize to 0-1
        
        # Sort by confidence score
        return sorted(contacts, key=lambda x: x['confidence'], reverse=True)
    
    def refresh_contacts_cache(self, user) -> int:
        """Refresh the entire contacts cache for a user"""
        try:
            # Clear existing cache
            ContactCache.objects.filter(user=user).delete()
            
            # Fetch all contacts
            url = f"{self.base_url}/people/me/connections"
            params = {
                'personFields': 'names,emailAddresses,phoneNumbers,photos',
                'pageSize': 1000
            }
            
            total_cached = 0
            next_page_token = None
            
            while True:
                if next_page_token:
                    params['pageToken'] = next_page_token
                
                response = requests.get(url, headers=self.headers, params=params)
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                connections = data.get('connections', [])
                
                for person in connections:
                    contact_info = self._extract_contact_info(person)
                    if contact_info:
                        self._cache_contact(user, person, contact_info)
                        total_cached += 1
                
                next_page_token = data.get('nextPageToken')
                if not next_page_token:
                    break
            
            return total_cached
            
        except Exception as e:
            print(f"Error refreshing contacts cache: {e}")
            return 0