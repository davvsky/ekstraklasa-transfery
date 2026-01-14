#!/usr/bin/env python3
"""
Simple API server for Ekstraklasa transfers
Serves transfer data without external dependencies
"""

import json
import http.server
import socketserver
import urllib.parse
from datetime import datetime
import os

class TransferAPI:
    def __init__(self):
        self.transfers = self.get_sample_transfers()
    
    def get_sample_transfers(self):
        """Get sample transfer data (will be replaced with scraped data)"""
        return [
            {
                "id": 1,
                "playerName": "Kacper Urbański",
                "type": "out",
                "fromTeam": "Legia Warszawa",
                "toTeam": "Bologna FC",
                "transferDate": "2025-01-12",
                "fee": "3.5M €",
                "summary": "Młody pomocnik Legii Warszawa przeniósł się do włoskiej Bologni. Transfer Urbańskiego to kolejny krok w rozwoju kariery 19-latka.",
                "sourceUrl": "https://www.90minut.pl/news/12345",
                "sourceName": "90minut.pl"
            },
            {
                "id": 2,
                "playerName": "Jean Carlos",
                "type": "in",
                "fromTeam": "Flamengo RJ",
                "toTeam": "Lech Poznań",
                "transferDate": "2025-01-10",
                "fee": "2.0M €",
                "summary": "Brazylijski napastnik dołączył do Lecha Poznań. Jean Carlos podpisał 3,5-letni kontrakt z mistrzem Polski.",
                "sourceUrl": "https://ekstraklasa.org/news/67890",
                "sourceName": "Ekstraklasa.org"
            },
            {
                "id": 3,
                "playerName": "Bartłomiej Wdowik",
                "type": "out",
                "fromTeam": "Raków Częstochowa",
                "toTeam": "FC Copenhagen",
                "transferDate": "2025-01-08",
                "fee": "1.8M €",
                "summary": "Obrońca Rakowa Częstochowa przeniósł się do duńskiego FC Copenhagen. Wdowik zagra w Danish Superliga.",
                "sourceUrl": "https://www.transfermarkt.pl/transfer/54321",
                "sourceName": "Transfermarkt.pl"
            },
            {
                "id": 4,
                "playerName": "Igor Sapała",
                "type": "in",
                "fromTeam": "Wolny agent",
                "toTeam": "Wisła Kraków",
                "transferDate": "2025-01-11",
                "fee": "Bez opłaty",
                "summary": "Były pomocnik Górnika Zabrze podpisał kontrakt z Wisłą Kraków. Sapała wzmocni środek pola Białej Gwiazdy.",
                "sourceUrl": "https://www.wislaportal.pl/news/98765",
                "sourceName": "WisłaPortal.pl"
            },
            {
                "id": 5,
                "playerName": "Adrián Kapráľ",
                "type": "out",
                "fromTeam": "Jagiellonia Białystok",
                "toTeam": "Slovan Bratysława",
                "transferDate": "2025-01-09",
                "fee": "500k €",
                "summary": "Słowacki pomocnik opuścił Jagiellonię Białystok i wrócił do Slovana Bratysława. Transfer na zasadzie wypożyczenia z opcją kupna.",
                "sourceUrl": "https://jagiellonia.pl/news/43210",
                "sourceName": "Jagiellonia.pl"
            }
        ]
    
    def get_transfers(self, team=None, transfer_type=None):
        """Get filtered transfers"""
        filtered_transfers = self.transfers
        
        if team:
            filtered_transfers = [t for t in filtered_transfers 
                                if t['fromTeam'] == team or t['toTeam'] == team]
        
        if transfer_type:
            filtered_transfers = [t for t in filtered_transfers 
                                if t['type'] == transfer_type]
        
        return filtered_transfers
    
    def get_teams(self):
        """Get all unique teams"""
        teams = set()
        for transfer in self.transfers:
            if transfer['fromTeam'] and transfer['fromTeam'] != 'Wolny agent':
                teams.add(transfer['fromTeam'])
            if transfer['toTeam'] and transfer['toTeam'] != 'Wolny agent':
                teams.add(transfer['toTeam'])
        return sorted(list(teams))

class APIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.api = TransferAPI()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/api/transfers':
            self.handle_transfers(parsed_path)
        elif parsed_path.path == '/api/teams':
            self.handle_teams()
        else:
            # Serve static files
            super().do_GET()
    
    def handle_transfers(self, parsed_path):
        """Handle transfers API endpoint"""
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        team = query_params.get('team', [None])[0]
        transfer_type = query_params.get('type', [None])[0]
        
        transfers = self.api.get_transfers(team, transfer_type)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(transfers, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def handle_teams(self):
        """Handle teams API endpoint"""
        teams = self.api.get_teams()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(teams, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def run_server():
    """Run the API server"""
    PORT = 8080
    
    with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
        print(f"Server running at http://localhost:{PORT}")
        print(f"API endpoints:")
        print(f"  - GET /api/transfers - Get all transfers")
        print(f"  - GET /api/transfers?team=Legia%20Warszawa - Filter by team")
        print(f"  - GET /api/transfers?type=in - Filter by transfer type")
        print(f"  - GET /api/teams - Get all teams")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()