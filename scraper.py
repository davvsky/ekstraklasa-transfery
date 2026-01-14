#!/usr/bin/env python3
"""
Ekstraklasa Transfer Scraper
Scrapes transfer information from various football sources
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse

class EkstraklasaScraper:
    def __init__(self):
        self.transfers = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_90minut(self):
        """Scrape transfers from 90minut.pl"""
        try:
            url = "https://www.90minut.pl/ekstraklasa/transfery.html"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for transfer tables
            transfer_rows = soup.find_all('tr', class_='transfer-row')
            
            for row in transfer_rows:
                try:
                    player_name = row.find('td', class_='player').text.strip()
                    from_team = row.find('td', class_='from').text.strip()
                    to_team = row.find('td', class_='to').text.strip()
                    transfer_type = 'in' if to_team and from_team != 'Wolny agent' else 'out'
                    transfer_date = row.find('td', class_='date').text.strip()
                    fee = row.find('td', class_='fee').text.strip()
                    
                    transfer = {
                        'playerName': player_name,
                        'type': transfer_type,
                        'fromTeam': from_team,
                        'toTeam': to_team,
                        'transferDate': self.parse_date(transfer_date),
                        'fee': fee or 'Nieznana',
                        'summary': f'{player_name} przeniósł się z {from_team} do {to_team}',
                        'sourceUrl': url,
                        'sourceName': '90minut.pl'
                    }
                    
                    self.transfers.append(transfer)
                    
                except Exception as e:
                    print(f"Error parsing transfer row: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping 90minut: {e}")
    
    def scrape_transfermarkt(self):
        """Scrape transfers from transfermarkt.pl"""
        try:
            url = "https://www.transfermarkt.pl/ekstraklasa/transfers/wettbewerb/PL1"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for transfer table
            transfer_table = soup.find('table', class_='items')
            if transfer_table:
                rows = transfer_table.find_all('tr', class_=lambda x: x and 'transfer-row' in x)
                
                for row in rows[1:]:  # Skip header row
                    try:
                        cells = row.find_all('td')
                        if len(cells) >= 6:
                            player_name = cells[0].text.strip()
                            from_team = cells[3].text.strip()
                            to_team = cells[4].text.strip()
                            transfer_type = 'in' if to_team and from_team != 'Wolny agent' else 'out'
                            transfer_date = cells[2].text.strip()
                            fee = cells[5].text.strip()
                            
                            transfer = {
                                'playerName': player_name,
                                'type': transfer_type,
                                'fromTeam': from_team,
                                'toTeam': to_team,
                                'transferDate': self.parse_date(transfer_date),
                                'fee': fee or 'Nieznana',
                                'summary': f'{player_name} przeniósł się z {from_team} do {to_team}',
                                'sourceUrl': url,
                                'sourceName': 'Transfermarkt.pl'
                            }
                            
                            self.transfers.append(transfer)
                            
                    except Exception as e:
                        print(f"Error parsing transfermarkt row: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error scraping transfermarkt: {e}")
    
    def scrape_ekstraklasa_org(self):
        """Scrape transfers from ekstraklasa.org"""
        try:
            url = "https://ekstraklasa.org/transfery/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for transfer news/articles
            transfer_articles = soup.find_all('article', class_='transfer-news')
            
            for article in transfer_articles:
                try:
                    title_elem = article.find('h2') or article.find('h3')
                    if not title_elem:
                        continue
                        
                    title = title_elem.text.strip()
                    link_elem = article.find('a')
                    article_url = urljoin(url, link_elem['href']) if link_elem else url
                    
                    # Extract player name from title
                    player_name = self.extract_player_name(title)
                    
                    # Try to get more details from the article
                    summary = article.find('p', class_='excerpt')
                    if summary:
                        summary_text = summary.text.strip()
                    else:
                        summary_text = title
                    
                    # Extract date
                    date_elem = article.find('time') or article.find('span', class_='date')
                    transfer_date = date_elem.text.strip() if date_elem else datetime.now().strftime('%d.%m.%Y')
                    
                    transfer = {
                        'playerName': player_name,
                        'type': self.determine_transfer_type(title),
                        'fromTeam': self.extract_team(title, 'from'),
                        'toTeam': self.extract_team(title, 'to'),
                        'transferDate': self.parse_date(transfer_date),
                        'fee': 'Nieznana',
                        'summary': summary_text,
                        'sourceUrl': article_url,
                        'sourceName': 'Ekstraklasa.org'
                    }
                    
                    self.transfers.append(transfer)
                    
                except Exception as e:
                    print(f"Error parsing ekstraklasa.org article: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error scraping ekstraklasa.org: {e}")
    
    def parse_date(self, date_str):
        """Parse various date formats to standard format"""
        try:
            # Remove common separators and normalize
            date_str = date_str.strip().replace('.', '-').replace('/', '-')
            
            # Try different formats
            formats = ['%d-%m-%Y', '%d-%m-%y', '%Y-%m-%d', '%d.%m.%Y', '%d.%m.%y']
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            # If no format matches, return today's date
            return datetime.now().strftime('%Y-%m-%d')
            
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
    
    def extract_player_name(self, title):
        """Extract player name from title"""
        # Simple extraction - look for capitalized words
        words = title.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Check if next word is also capitalized (might be part of name)
                name = word
                if i + 1 < len(words) and words[i + 1][0].isupper():
                    name += ' ' + words[i + 1]
                return name
        return "Nieznany zawodnik"
    
    def determine_transfer_type(self, title):
        """Determine if it's incoming or outgoing transfer"""
        outgoing_keywords = ['opuszcza', 'odchodzi', 'sprzedany', 'wypożyczony', 'żegna się']
        incoming_keywords = ['dołącza', 'podpisuje', 'przychodzi', 'zatrudnia', 'transfer do']
        
        title_lower = title.lower()
        
        for keyword in outgoing_keywords:
            if keyword in title_lower:
                return 'out'
        
        for keyword in incoming_keywords:
            if keyword in title_lower:
                return 'in'
        
        return 'in'  # Default to incoming
    
    def extract_team(self, title, direction):
        """Extract team name from title"""
        ekstraklasa_teams = [
            'Legia Warszawa', 'Lech Poznań', 'Wisła Kraków', 'Lechia Gdańsk',
            'Jagiellonia Białystok', 'Cracovia', 'Śląsk Wrocław', 'Pogoń Szczecin',
            'Górnik Zabrze', 'Raków Częstochowa', 'Bruk-Bet Termalica Nieciecza',
            'Stal Mielec', 'Warta Poznań', 'Radomiak Radom', 'Korona Kielce'
        ]
        
        for team in ekstraklasa_teams:
            if team.lower() in title.lower():
                return team
        
        return "Nieznana drużyna"
    
    def save_to_json(self, filename='transfers.json'):
        """Save transfers to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.transfers, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(self.transfers)} transfers to {filename}")
    
    def run(self):
        """Run all scrapers"""
        print("Starting Ekstraklasa transfer scraping...")
        
        # Scrape different sources
        print("Scraping 90minut.pl...")
        self.scrape_90minut()
        
        print("Scraping Transfermarkt.pl...")
        self.scrape_transfermarkt()
        
        print("Scraping Ekstraklasa.org...")
        self.scrape_ekstraklasa_org()
        
        # Remove duplicates based on player name and teams
        self.transfers = self.remove_duplicates()
        
        # Sort by date
        self.transfers.sort(key=lambda x: x['transferDate'], reverse=True)
        
        # Save to file
        self.save_to_json()
        
        print(f"Scraping completed. Found {len(self.transfers)} unique transfers.")
    
    def remove_duplicates(self):
        """Remove duplicate transfers"""
        seen = set()
        unique_transfers = []
        
        for transfer in self.transfers:
            # Create a unique key based on player name and teams
            key = f"{transfer['playerName']}-{transfer['fromTeam']}-{transfer['toTeam']}"
            
            if key not in seen:
                seen.add(key)
                unique_transfers.append(transfer)
        
        return unique_transfers

if __name__ == "__main__":
    scraper = EkstraklasaScraper()
    scraper.run()