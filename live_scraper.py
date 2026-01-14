#!/usr/bin/env python3
"""
Real Web Scraper for Ekstraklasa Transfers
Pulls actual transfer data from football websites
Uses requests and BeautifulSoup for reliable scraping
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time

class RealTransferScraper:
    def __init__(self):
        self.transfers = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Ekstraklasa teams for filtering
        self.ekstraklasa_teams = {
            'Legia Warszawa', 'Lech Poznań', 'Wisła Kraków', 'Lechia Gdańsk',
            'Jagiellonia Białystok', 'Cracovia', 'Śląsk Wrocław', 'Pogoń Szczecin',
            'Górnik Zabrze', 'Raków Częstochowa', 'Bruk-Bet Termalica Nieciecza',
            'Stal Mielec', 'Warta Poznań', 'Radomiak Radom', 'Korona Kielce',
            'Wisła Płock', 'ŁKS Łódź', 'Zagłębie Lubin'
        }
    
    def scrape_90minut_news(self):
        """Scrape transfer news from 90minut.pl"""
        print("Scraping 90minut.pl for transfer news...")
        
        try:
            # Main news page
            url = "https://www.90minut.pl"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for news articles with transfer keywords
            news_items = soup.find_all('article') or soup.find_all('div', class_='news-item')
            
            transfer_keywords = [
                'transfer', 'przenosi się', 'dołącza', 'odejdzie', 'wypożyczony',
                'transferuje', 'sprzedany', 'kupiony', 'kontrakt'
            ]
            
            for item in news_items:
                try:
                    title_elem = item.find('h2') or item.find('h3') or item.find('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Check if it's transfer-related
                    if not any(keyword in title.lower() for keyword in transfer_keywords):
                        continue
                    
                    link_elem = item.find('a')
                    if not link_elem or not link_elem.get('href'):
                        continue
                    
                    link = urljoin(url, link_elem['href'])
                    
                    # Get article details
                    transfer = self.extract_90minut_transfer(link, title)
                    if transfer:
                        self.transfers.append(transfer)
                    
                    # Be respectful to server
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error parsing news item: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping 90minut.pl: {e}")
    
    def extract_90minut_transfer(self, url, title):
        """Extract transfer details from 90minut article"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract player name
            player_name = self.extract_player_name(title)
            
            # Extract transfer details from article text
            article_text = soup.get_text()
            
            # Determine transfer type
            transfer_type = self.determine_transfer_type(title + ' ' + article_text)
            
            # Extract teams
            teams = self.extract_teams_from_text(title + ' ' + article_text)
            
            # Extract fee
            fee = self.extract_fee_from_text(article_text)
            
            # Extract date
            date_elem = soup.find('time') or soup.find('span', class_='date')
            if date_elem:
                transfer_date = self.parse_date(date_elem.get_text())
            else:
                transfer_date = datetime.now().strftime('%Y-%m-%d')
            
            transfer = {
                'id': len(self.transfers) + 1,
                'playerName': player_name,
                'type': transfer_type,
                'fromTeam': teams.get('from', 'Nieznana'),
                'toTeam': teams.get('to', 'Nieznana'),
                'transferDate': transfer_date,
                'fee': fee,
                'summary': title,
                'sourceUrl': url,
                'sourceName': '90minut.pl'
            }
            
            return transfer
            
        except Exception as e:
            print(f"Error extracting transfer from {url}: {e}")
            return None
    
    def scrape_transfermarkt_ekstraklasa(self):
        """Scrape Ekstraklasa transfers from Transfermarkt"""
        print("Scraping Transfermarkt.pl for Ekstraklasa transfers...")
        
        try:
            url = "https://www.transfermarkt.pl/ekstraklasa/transfers/wettbewerb/PL1"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find transfer table
            table = soup.find('table', class_='items')
            if not table:
                print("Transfer table not found on Transfermarkt")
                return
            
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header
                try:
                    cells = row.find_all('td')
                    if len(cells) < 6:
                        continue
                    
                    # Extract player name
                    player_cell = cells[0]
                    player_link = player_cell.find('a')
                    if not player_link:
                        continue
                    
                    player_name = player_link.get_text(strip=True)
                    
                    # Extract clubs
                    from_cell = cells[3]
                    to_cell = cells[4]
                    
                    from_team = from_cell.get_text(strip=True)
                    to_team = to_cell.get_text(strip=True)
                    
                    # Only include if at least one is Ekstraklasa team
                    if (from_team not in self.ekstraklasa_teams and 
                        to_team not in self.ekstraklasa_teams):
                        continue
                    
                    # Extract fee
                    fee_cell = cells[5] if len(cells) > 5 else None
                    fee = fee_cell.get_text(strip=True) if fee_cell else 'Nieznana'
                    
                    # Extract date
                    date_cell = cells[2] if len(cells) > 2 else None
                    date_str = date_cell.get_text(strip=True) if date_cell else ''
                    
                    transfer_date = self.parse_date(date_str)
                    
                    # Determine transfer type
                    transfer_type = 'in' if to_team in self.ekstraklasa_teams else 'out'
                    
                    transfer = {
                        'id': len(self.transfers) + 1,
                        'playerName': player_name,
                        'type': transfer_type,
                        'fromTeam': from_team,
                        'toTeam': to_team,
                        'transferDate': transfer_date,
                        'fee': fee,
                        'summary': f'{player_name}: {from_team} → {to_team}',
                        'sourceUrl': url,
                        'sourceName': 'Transfermarkt.pl'
                    }
                    
                    self.transfers.append(transfer)
                    
                except Exception as e:
                    print(f"Error parsing Transfermarkt row: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping Transfermarkt: {e}")
    
    def scrape_ekstraklasa_org(self):
        """Scrape transfers from official Ekstraklasa site"""
        print("Scraping Ekstraklasa.org...")
        
        try:
            url = "https://ekstraklasa.org/transfery/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for transfer news
            articles = soup.find_all('article') or soup.find_all('div', class_='transfer-item')
            
            for article in articles:
                try:
                    title_elem = article.find('h2') or article.find('h3')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    link_elem = article.find('a')
                    if not link_elem or not link_elem.get('href'):
                        continue
                    
                    link = urljoin(url, link_elem['href'])
                    
                    # Extract transfer details
                    transfer = self.extract_ekstraklasa_org_transfer(link, title)
                    if transfer:
                        self.transfers.append(transfer)
                    
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error parsing Ekstraklasa.org article: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping Ekstraklasa.org: {e}")
    
    def extract_ekstraklasa_org_transfer(self, url, title):
        """Extract transfer from Ekstraklasa.org article"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            player_name = self.extract_player_name(title)
            transfer_type = self.determine_transfer_type(title)
            
            article_text = soup.get_text()
            teams = self.extract_teams_from_text(title + ' ' + article_text)
            fee = self.extract_fee_from_text(article_text)
            
            transfer = {
                'id': len(self.transfers) + 1,
                'playerName': player_name,
                'type': transfer_type,
                'fromTeam': teams.get('from', 'Nieznana'),
                'toTeam': teams.get('to', 'Nieznana'),
                'transferDate': datetime.now().strftime('%Y-%m-%d'),
                'fee': fee,
                'summary': title,
                'sourceUrl': url,
                'sourceName': 'Ekstraklasa.org'
            }
            
            return transfer
            
        except Exception as e:
            print(f"Error extracting Ekstraklasa.org transfer: {e}")
            return None
    
    def extract_player_name(self, text):
        """Extract player name from text"""
        # Look for capitalized names
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in ['transfer', 'do', 'z', 'w', 'na', 'dołącza', 'opuszcza']:
                continue
                
            if len(word) > 2 and word[0].isupper():
                name = word
                if i + 1 < len(words) and len(words[i + 1]) > 2 and words[i + 1][0].isupper():
                    name += ' ' + words[i + 1]
                return name
        
        return "Nieznany zawodnik"
    
    def determine_transfer_type(self, text):
        """Determine transfer type from text"""
        text_lower = text.lower()
        
        outgoing = ['opuszcza', 'odchodzi', 'sprzedany', 'wypożyczony', 'żegna się', 'transfer do']
        incoming = ['dołącza', 'podpisuje', 'przychodzi', 'zatrudnia', 'transfer z', 'nowym zawodnikiem']
        
        for keyword in outgoing:
            if keyword in text_lower:
                return 'out'
        
        for keyword in incoming:
            if keyword in text_lower:
                return 'in'
        
        return 'in'  # Default
    
    def extract_teams_from_text(self, text):
        """Extract team names from text"""
        teams = {'from': None, 'to': None}
        
        text_lower = text.lower()
        
        # Look for Ekstraklasa teams in text
        for team in self.ekstraklasa_teams:
            if team.lower() in text_lower:
                # Check context to determine from/to
                if any(word in text_lower for word in ['do ' + team.lower(), team.lower() + ' dołącza', 'transfer do ' + team.lower()]):
                    teams['to'] = team
                elif any(word in text_lower for word in ['z ' + team.lower(), team.lower() + ' opuszcza', team.lower() + ' sprzedany']):
                    teams['from'] = team
        
        return teams
    
    def extract_fee_from_text(self, text):
        """Extract transfer fee from text"""
        # Fee patterns
        patterns = [
            r'(\d+\.?\d*)\s*m(?:ilion)?\s*€',  # X.X million euros
            r'(\d+)\s*tys(?:iąc|.)?\s*€',  # X thousand euros
            r'bezpłatnie',  # free
            r'wolny.*agent',  # free agent
            r'wypożyczenie',  # loan
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'bezpłatnie' in pattern or 'wolny' in pattern:
                    return 'Bez opłaty'
                elif 'wypożyczenie' in pattern:
                    return 'Wypożyczenie'
                else:
                    return match.group(0)
        
        return 'Nieznana'
    
    def parse_date(self, date_str):
        """Parse various date formats"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        # Common formats
        formats = [
            '%d.%m.%Y', '%d.%m.%y',
            '%d/%m/%Y', '%d/%m/%y',
            '%d-%m-%Y', '%d-%m-%y',
            '%Y-%m-%d'
        ]
        
        date_str = date_str.strip()
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Try to extract today/yesterday/tomorrow
        date_str_lower = date_str.lower()
        if 'dzisiaj' in date_str_lower or 'today' in date_str_lower:
            return datetime.now().strftime('%Y-%m-%d')
        elif 'wczoraj' in date_str_lower or 'yesterday' in date_str_lower:
            return (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        return datetime.now().strftime('%Y-%m-%d')
    
    def deduplicate_transfers(self):
        """Remove duplicate transfers"""
        seen = set()
        unique_transfers = []
        
        for transfer in self.transfers:
            # Create unique key
            key = f"{transfer['playerName'].lower()}-{transfer['fromTeam']}-{transfer['toTeam']}"
            
            if key not in seen:
                seen.add(key)
                unique_transfers.append(transfer)
        
        return unique_transfers
    
    def save_transfers(self, filename='transfers.json'):
        """Save transfers to JSON"""
        # Remove duplicates
        self.transfers = self.deduplicate_transfers()
        
        # Sort by date
        self.transfers.sort(key=lambda x: x.get('transferDate', ''), reverse=True)
        
        # Limit to recent transfers
        cutoff_date = datetime.now() - timedelta(days=90)  # Last 3 months
        recent_transfers = []
        
        for transfer in self.transfers:
            try:
                transfer_date = datetime.strptime(transfer['transferDate'], '%Y-%m-%d')
                if transfer_date >= cutoff_date:
                    recent_transfers.append(transfer)
            except:
                recent_transfers.append(transfer)
        
        # Limit to 50 most recent
        self.transfers = recent_transfers[:50]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.transfers, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(self.transfers)} unique transfers to {filename}")
        return self.transfers
    
    def run(self):
        """Run the real scraper"""
        print("Starting real web scraping...")
        print("=" * 50)
        
        try:
            # Scrape multiple sources
            self.scrape_90minut_news()
            time.sleep(2)  # Be respectful
            
            self.scrape_transfermarkt_ekstraklasa()
            time.sleep(2)
            
            self.scrape_ekstraklasa_org()
            
        except Exception as e:
            print(f"Scraping error: {e}")
        
        # Save results
        transfers = self.save_transfers()
        
        print(f"\nScraping completed!")
        print(f"Found {len(transfers)} real transfers")
        print("=" * 50)
        
        # Show some stats
        incoming = len([t for t in transfers if t['type'] == 'in'])
        outgoing = len([t for t in transfers if t['type'] == 'out'])
        
        print(f"Incoming transfers: {incoming}")
        print(f"Outgoing transfers: {outgoing}")
        print(f"Total: {len(transfers)}")
        
        return transfers

if __name__ == "__main__":
    scraper = RealTransferScraper()
    transfers = scraper.run()