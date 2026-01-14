#!/usr/bin/env python3
"""
Real Ekstraklasa Transfer Scraper
Scrapes actual transfer data from Polish football websites
Works with GitHub Actions for automatic updates
"""

import json
import re
import time
from datetime import datetime, timedelta
from urllib.parse import urljoin

# We'll use built-in libraries for GitHub Actions compatibility
import urllib.request
import urllib.error
from html.parser import HTMLParser

class TransferScraper:
    def __init__(self):
        self.transfers = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Ekstraklasa teams for filtering
        self.ekstraklasa_teams = {
            'Legia Warszawa', 'Lech Poznań', 'Wisła Kraków', 'Lechia Gdańsk',
            'Jagiellonia Białystok', 'Cracovia', 'Śląsk Wrocław', 'Pogoń Szczecin',
            'Górnik Zabrze', 'Raków Częstochowa', 'Bruk-Bet Termalica Nieciecza',
            'Stal Mielec', 'Warta Poznań', 'Radomiak Radom', 'Korona Kielce',
            'Wisła Płock', 'ŁKS Łódź', 'Zagłębie Lubin', 'GKS Katowice'
        }
    
    def fetch_page(self, url, retries=3):
        """Fetch webpage with retries"""
        for attempt in range(retries):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=10) as response:
                    return response.read().decode('utf-8', errors='ignore')
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2)
        return None
    
    def parse_90minut_transfers(self):
        """Scrape 90minut.pl transfer news"""
        print("Scraping 90minut.pl...")
        
        # Main 90minut page
        main_url = "https://www.90minut.pl"
        html = self.fetch_page(main_url)
        
        if not html:
            print("Failed to fetch 90minut.pl")
            return
        
        # Look for transfer news in the main page
        # 90minut uses specific patterns for transfer news
        transfer_keywords = ['transfer', 'przenosi się', 'dołącza', 'odejdzie', 'wypożyczony']
        
        # Simplified approach: look for transfer-related headlines
        headlines = re.findall(r'<a[^>]*class="[^"]*news[^"]*"[^>]*href="([^"]*)"[^>]*>([^<]*transfer[^<]*)</a>', html, re.IGNORECASE)
        
        for href, title in headlines:
            if any(keyword in title.lower() for keyword in transfer_keywords):
                full_url = urljoin(main_url, href)
                
                # Try to extract player info from title
                player_name = self.extract_player_name(title)
                
                # Determine transfer type
                transfer_type = self.determine_transfer_type(title)
                
                # Get more details
                details = self.extract_transfer_details(title)
                
                transfer = {
                    'id': len(self.transfers) + 1,
                    'playerName': player_name,
                    'type': transfer_type,
                    'fromTeam': details.get('from_team', 'Nieznana'),
                    'toTeam': details.get('to_team', 'Nieznana'),
                    'transferDate': datetime.now().strftime('%Y-%m-%d'),
                    'fee': details.get('fee', 'Nieznana'),
                    'summary': title.strip(),
                    'sourceUrl': full_url,
                    'sourceName': '90minut.pl'
                }
                
                self.transfers.append(transfer)
    
    def parse_transfermarkt_ekstraklasa(self):
        """Scrape Ekstraklasa transfers from Transfermarkt"""
        print("Scraping Transfermarkt...")
        
        url = "https://www.transfermarkt.pl/ekstraklasa/transfers/wettbewerb/PL1"
        html = self.fetch_page(url)
        
        if not html:
            print("Failed to fetch Transfermarkt")
            return
        
        # Look for recent transfers
        # Transfermarkt has specific table structure
        rows = re.findall(r'<tr[^>]*class="[^"]*transfer-row[^"]*"[^>]*>.*?</tr>', html, re.DOTALL)
        
        for row in rows:
            try:
                # Extract player name
                player_match = re.search(r'<a[^>]*class="[^"]*spielname[^"]*"[^>]*>([^<]+)</a>', row)
                if not player_match:
                    continue
                
                player_name = player_match.group(1).strip()
                
                # Extract teams
                from_team_match = re.search(r'<td[^>]*class="[^"]*verein[^"]*"[^>]*>([^<]+)</td>', row)
                to_team_match = re.search(r'<td[^>]*class="[^"]*verein[^"]*"[^>]*>([^<]+)</td>', row)
                
                # Extract fee
                fee_match = re.search(r'<td[^>]*class="[^"]*Ablöse[^"]*"[^>]*>([^<]+)</td>', row)
                fee = fee_match.group(1).strip() if fee_match else 'Nieznana'
                
                # Extract date
                date_match = re.search(r'<td[^>]*class="[^"]*datum[^"]*"[^>]*>([^<]+)</td>', row)
                date_str = date_match.group(1).strip() if date_match else ''
                
                transfer = {
                    'id': len(self.transfers) + 1,
                    'playerName': player_name,
                    'type': 'in',  # Default to incoming for now
                    'fromTeam': from_team_match.group(1).strip() if from_team_match else 'Nieznana',
                    'toTeam': to_team_match.group(1).strip() if to_team_match else 'Nieznana',
                    'transferDate': self.parse_date(date_str),
                    'fee': fee,
                    'summary': f'{player_name} transfer between clubs',
                    'sourceUrl': url,
                    'sourceName': 'Transfermarkt.pl'
                }
                
                self.transfers.append(transfer)
                
            except Exception as e:
                print(f"Error parsing transfer row: {e}")
                continue
    
    def get_recent_club_transfers(self):
        """Get transfers from official Ekstraklasa club websites"""
        print("Scraping club websites...")
        
        # Club websites that have transfer news
        club_websites = [
            ('Legia Warszawa', 'https://legia.com'),
            ('Lech Poznań', 'https://www.lechpoznan.pl'),
            ('Wisła Kraków', 'https://www.wisla.krakow.pl'),
            ('Raków Częstochowa', 'https://www.rakow.com.pl'),
            ('Śląsk Wrocław', 'https://slaskwroclaw.com'),
        ]
        
        for club_name, club_url in club_websites:
            try:
                html = self.fetch_page(club_url)
                if not html:
                    continue
                
                # Look for transfer news
                transfer_links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*transfer[^<]*)</a>', html, re.IGNORECASE)
                
                for link, title in transfer_links:
                    full_url = urljoin(club_url, link)
                    player_name = self.extract_player_name(title)
                    transfer_type = self.determine_transfer_type(title)
                    
                    transfer = {
                        'id': len(self.transfers) + 1,
                        'playerName': player_name,
                        'type': transfer_type,
                        'fromTeam': club_name if transfer_type == 'out' else 'Nieznana',
                        'toTeam': club_name if transfer_type == 'in' else 'Nieznana',
                        'transferDate': datetime.now().strftime('%Y-%m-%d'),
                        'fee': 'Nieznana',
                        'summary': title.strip(),
                        'sourceUrl': full_url,
                        'sourceName': f'{club_name} - Oficjalna strona'
                    }
                    
                    self.transfers.append(transfer)
                    
            except Exception as e:
                print(f"Error scraping {club_name}: {e}")
                continue
    
    def extract_player_name(self, text):
        """Extract player name from text"""
        # Look for capitalized names (simplified approach)
        words = text.split()
        for i, word in enumerate(words):
            # Skip if it's a common word
            if word.lower() in ['transfer', 'do', 'z', 'w', 'na', 'dołącza', 'opuszcza', 'przenosi']:
                continue
                
            # Look for capitalized words that might be names
            if len(word) > 2 and word[0].isupper():
                # Check if next word is also capitalized (might be full name)
                name = word
                if i + 1 < len(words) and len(words[i + 1]) > 2 and words[i + 1][0].isupper():
                    name += ' ' + words[i + 1]
                return name
        
        return "Nieznany zawodnik"
    
    def determine_transfer_type(self, text):
        """Determine if it's incoming or outgoing transfer"""
        text_lower = text.lower()
        
        outgoing_keywords = ['opuszcza', 'odchodzi', 'sprzedany', 'wypożyczony', 'żegna się', 'transfer do']
        incoming_keywords = ['dołącza', 'podpisuje', 'przychodzi', 'zatrudnia', 'transfer z', 'nowym zawodnikiem']
        
        for keyword in outgoing_keywords:
            if keyword in text_lower:
                return 'out'
        
        for keyword in incoming_keywords:
            if keyword in text_lower:
                return 'in'
        
        # Default based on context
        return 'in'
    
    def extract_transfer_details(self, title):
        """Extract transfer details from title"""
        details = {}
        
        # Look for team names
        teams_found = []
        for team in self.ekstraklasa_teams:
            if team.lower() in title.lower():
                teams_found.append(team)
        
        if len(teams_found) >= 1:
            details['to_team'] = teams_found[0]  # Assume first found is destination
        
        # Look for fee information
        fee_patterns = [
            r'(\d+\.?\d*)\s*m\s*€',  # X.XM €
            r'(\d+)\s*tys',  # X tys
            r'bezpłatnie',  # free
            r'wolny',  # free agent
        ]
        
        for pattern in fee_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                if 'bezpłatnie' in pattern or 'wolny' in pattern:
                    details['fee'] = 'Bez opłaty'
                else:
                    details['fee'] = match.group(0)
                break
        
        return details
    
    def parse_date(self, date_str):
        """Parse various date formats"""
        try:
            # Common Polish date formats
            formats = [
                '%d.%m.%Y', '%d.%m.%y',
                '%d/%m/%Y', '%d/%m/%y',
                '%d-%m-%Y', '%d-%m-%y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
                except ValueError:
                    continue
                    
        except Exception:
            pass
            
        return datetime.now().strftime('%Y-%m-%d')
    
    def deduplicate_transfers(self):
        """Remove duplicate transfers"""
        seen = set()
        unique_transfers = []
        
        for transfer in self.transfers:
            # Create unique key based on player name and teams
            key = f"{transfer['playerName'].lower()}-{transfer['fromTeam']}-{transfer['toTeam']}"
            
            if key not in seen:
                seen.add(key)
                unique_transfers.append(transfer)
        
        return unique_transfers
    
    def save_transfers(self, filename='transfers.json'):
        """Save transfers to JSON file"""
        # Remove duplicates
        self.transfers = self.deduplicate_transfers()
        
        # Sort by date
        self.transfers.sort(key=lambda x: x.get('transferDate', ''), reverse=True)
        
        # Limit to most recent 50 transfers
        self.transfers = self.transfers[:50]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.transfers, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(self.transfers)} transfers to {filename}")
        return self.transfers
    
    def generate_html_data(self):
        """Generate JavaScript data for HTML embedding"""
        # Remove duplicates and sort
        self.transfers = self.deduplicate_transfers()
        self.transfers.sort(key=lambda x: x.get('transferDate', ''), reverse=True)
        
        # Generate JS array
        js_data = "const transfers = " + json.dumps(self.transfers, ensure_ascii=False, indent=2) + ";"
        
        return js_data
    
    def run(self):
        """Run the scraper"""
        print("Starting Ekstraklasa transfer scraping...")
        
        try:
            # Scrape different sources
            self.parse_90minut_transfers()
            time.sleep(1)  # Be respectful to servers
            
            self.parse_transfermarkt_ekstraklasa()
            time.sleep(1)
            
            self.get_recent_club_transfers()
            
        except Exception as e:
            print(f"Scraping error: {e}")
        
        # Save results
        transfers = self.save_transfers()
        return transfers

if __name__ == "__main__":
    scraper = TransferScraper()
    transfers = scraper.run()
    
    print(f"\nScraping completed! Found {len(transfers)} transfers.")
    
    # Generate HTML update
    js_data = scraper.generate_html_data()
    with open('transfer_data.js', 'w', encoding='utf-8') as f:
        f.write(js_data)
    
    print("Generated transfer_data.js for HTML embedding")