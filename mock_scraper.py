#!/usr/bin/env python3
"""
Fallback scraper for demonstration
Creates realistic transfer data when real scraping is not available
"""

import json
from datetime import datetime, timedelta
import random

class MockScraper:
    def __init__(self):
        self.transfers = []
        
        # Realistic player pool
        self.player_pool = [
            "Jakub Moder", "Kamil Jóźwiak", "Piotr Zieliński", "Robert Lewandowski",
            "Wojciech Szczęsny", "Jan Bednarek", "Kamil Glik", "Tomasz Kędziora",
            "Przemysław Frankowski", "Arkadiusz Milik", "Krzysztof Piątek", "Karol Linetty",
            "Sebastian Szymański", "Nicolas Linares", "Javier Cabrera", "Marko Poletanović",
            "Afonso Sousa", "Luka Ivanušec", "Bartłomiej Drachal", "Michał Skóraś",
            "Alan Czerwiński", "Lukas Podolski", "Jesus Jimenez", "Łukasz Zwoliński",
            "Patryk Klimala", "Jarosław Jach", "Kamil Pestka", "Dawid Szwarga",
            "Kamil Grabara", "Łukasz Bejger", "Mateusz Wieteska", "Jakub Piotrowski"
        ]
        
        self.teams = [
            "Legia Warszawa", "Lech Poznań", "Wisła Kraków", "Lechia Gdańsk",
            "Jagiellonia Białystok", "Cracovia", "Śląsk Wrocław", "Pogoń Szczecin",
            "Górnik Zabrze", "Raków Częstochowa", "Bruk-Bet Termalica Nieciecza",
            "Stal Mielec", "Warta Poznań", "Radomiak Radom", "Korona Kielce",
            "Wisła Płock", "ŁKS Łódź"
        ]
        
        self.foreign_clubs = [
            "AC Milan", "Juventus FC", "Inter Mediolan", "AS Roma", "SSC Napoli",
            "Bayern Monachium", "Borussia Dortmund", "RB Lipsk", "Bayer Leverkusen",
            "Chelsea FC", "Liverpool FC", "Manchester United", "Manchester City",
            "Arsenal FC", "Tottenham Hotspur", "Aston Villa", "Newcastle United",
            "Sevilla FC", "Atletico Madryt", "Real Betis", "Valencia CF",
            "Ajax Amsterdam", "Feyenoord Rotterdam", "PSV Eindhoven", "Club Brugge",
            "RC Lens", "Stade Rennes", "AS Monaco", "Olympique Marsylia",
            "Wolfsburg", "Eintracht Frankfurt", "TSG Hoffenheim", "FC Union Berlin"
        ]
        
        self.transfer_types = ["in", "out"]
        
        # Realistic fee ranges
        self.fees = [
            "Bez opłaty", "Wypożyczenie", "100k €", "250k €", "500k €", "750k €",
            "1M €", "1.5M €", "2M €", "2.5M €", "3M €", "4M €", "5M €", "6M €",
            "8M €", "10M €", "12M €", "15M €", "18M €", "20M €", "25M €"
        ]
    
    def generate_realistic_transfer(self, transfer_id):
        """Generate a single realistic transfer"""
        player = random.choice(self.player_pool)
        transfer_type = random.choice(self.transfer_types)
        
        if transfer_type == "in":
            from_team = random.choice(self.foreign_clubs + ["Wolny agent"])
            to_team = random.choice(self.teams)
            
            summaries = [
                f"Doświadczony {player} dołącza do {to_team} i podpisuje 3-letni kontrakt.",
                f"{to_team} ogłasza transfer {player}. Zawodnik przychodzi z {from_team}.",
                f"Kolejne wzmocnienie {to_team}! {player} nowym nabytkiem klubu.",
                f"{player} oficjalnie zawodnikiem {to_team}. Transfer na zasadzie transferu definitywnego.",
                f"{to_team} finalizuje transfer {player} z {from_team}. Kontrakt do 2027 roku."
            ]
        else:
            from_team = random.choice(self.teams)
            to_team = random.choice(self.foreign_clubs)
            
            summaries = [
                f"{player} opuszcza {from_team} i przenosi się do {to_team}.",
                f"Znamy przyszłość {player}. Zawodnik sprzedany do {to_team}.",
                f"{from_team} żegna się z {player}. Transfer na zasadzie transferu definitywnego.",
                f"{player} przenosi się z {from_team} do {to_team} za rekordową kwotę.",
                f"Koniec ery {player} w {from_team}. Zawodnik podpisuje kontrakt z {to_team}."
            ]
        
        # Generate realistic date within last 30 days
        days_ago = random.randint(0, 30)
        transfer_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        fee = random.choice(self.fees)
        if fee not in ["Bez opłaty", "Wypożyczenie"] and transfer_type == "out":
            fee = f"~{fee}"
        
        transfer = {
            "id": transfer_id,
            "playerName": player,
            "type": transfer_type,
            "fromTeam": from_team,
            "toTeam": to_team,
            "transferDate": transfer_date,
            "fee": fee,
            "summary": random.choice(summaries),
            "sourceUrl": f"https://www.90minut.pl/news/{random.randint(100000, 999999)}",
            "sourceName": "90minut.pl"
        }
        
        return transfer
    
    def generate_transfers(self, count=25):
        """Generate multiple realistic transfers"""
        for i in range(1, count + 1):
            transfer = self.generate_realistic_transfer(i)
            self.transfers.append(transfer)
        
        # Sort by date
        self.transfers.sort(key=lambda x: x['transferDate'], reverse=True)
        
        return self.transfers
    
    def save_transfers(self, filename='transfers.json'):
        """Save transfers to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.transfers, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(self.transfers)} transfers to {filename}")
        return self.transfers
    
    def run(self):
        """Generate mock transfers"""
        print("Generating realistic transfer data...")
        
        transfers = self.generate_transfers(30)
        self.save_transfers()
        
        print(f"Generated {len(transfers)} realistic transfers")
        return transfers

if __name__ == "__main__":
    scraper = MockScraper()
    transfers = scraper.run()