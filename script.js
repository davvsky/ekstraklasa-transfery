class EkstraklasaTransfers {
    constructor() {
        this.transfers = [];
        this.teams = [];
        this.filters = {
            team: '',
            type: ''
        };
        this.init();
    }

    async init() {
        await this.loadTransfers();
        this.setupFilters();
        this.renderTransfers();
    }

    async loadTransfers() {
        try {
            // Load data from API
            const response = await fetch('/api/transfers');
            if (!response.ok) {
                throw new Error('Failed to fetch transfers');
            }
            this.transfers = await response.json();
            await this.loadTeams();
        } catch (error) {
            console.error('Error loading transfers:', error);
            this.showError('Nie udało się załadować danych transferowych');
        }
    }

    getMockTransfers() {
        return [
            {
                id: 1,
                playerName: "Jan Kowalski",
                type: "in",
                fromTeam: "Legia Warszawa",
                toTeam: "Lech Poznań",
                transferDate: "2025-01-10",
                fee: "2.5M €",
                summary: "Doświadczony napastnik dołączył do Lecha Poznań, podpisując 3-letni kontrakt. Kowalski ma wzmocnić atak drużyny w walce o mistrzostwo.",
                sourceUrl: "https://example.com/transfer1",
                sourceName: "Ekstraklasa.org"
            },
            {
                id: 2,
                playerName: "Piotr Nowak",
                type: "out",
                fromTeam: "Lech Poznań",
                toTeam: "AC Milan",
                transferDate: "2025-01-08",
                fee: "8M €",
                summary: "Młody pomocnik przeniósł się do włoskiego giganta. Transfer Nowaka to jeden z najdroższych w historii Ekstraklasy.",
                sourceUrl: "https://example.com/transfer2",
                sourceName: "Sport.pl"
            },
            {
                id: 3,
                playerName: "Adam Wiśniewski",
                type: "in",
                fromTeam: "Wolny agent",
                toTeam: "Wisła Kraków",
                transferDate: "2025-01-12",
                fee: "Bez opłaty",
                summary: "Były reprezentant Polski podpisał kontrakt z Wisłą po rozwiązaniu umowy z poprzednim klubem.",
                sourceUrl: "https://example.com/transfer3",
                sourceName: "Wiara.pl"
            }
        ];
    }

    async loadTeams() {
        try {
            const response = await fetch('/api/teams');
            if (!response.ok) {
                throw new Error('Failed to fetch teams');
            }
            this.teams = await response.json();
        } catch (error) {
            console.error('Error loading teams:', error);
            // Fallback to extracting from transfers
            this.extractTeams();
        }
    }

    extractTeams() {
        const teamSet = new Set();
        this.transfers.forEach(transfer => {
            if (transfer.fromTeam && transfer.fromTeam !== "Wolny agent") {
                teamSet.add(transfer.fromTeam);
            }
            if (transfer.toTeam && transfer.toTeam !== "Wolny agent") {
                teamSet.add(transfer.toTeam);
            }
        });
        this.teams = Array.from(teamSet).sort();
    }

    setupFilters() {
        const teamFilter = document.getElementById('team-filter');
        const typeFilter = document.getElementById('transfer-type');

        // Populate team filter
        this.teams.forEach(team => {
            const option = document.createElement('option');
            option.value = team;
            option.textContent = team;
            teamFilter.appendChild(option);
        });

        // Add event listeners
        teamFilter.addEventListener('change', (e) => {
            this.filters.team = e.target.value;
            this.renderTransfers();
        });

        typeFilter.addEventListener('change', (e) => {
            this.filters.type = e.target.value;
            this.renderTransfers();
        });
    }

    getFilteredTransfers() {
        return this.transfers.filter(transfer => {
            const teamMatch = !this.filters.team || 
                transfer.fromTeam === this.filters.team || 
                transfer.toTeam === this.filters.team;
            
            const typeMatch = !this.filters.type || 
                transfer.type === this.filters.type;
            
            return teamMatch && typeMatch;
        });
    }

    renderTransfers() {
        const container = document.getElementById('transfers-container');
        const filteredTransfers = this.getFilteredTransfers();

        if (filteredTransfers.length === 0) {
            container.innerHTML = '<div class="no-results">Brak transferów spełniających kryteria filtrowania</div>';
            return;
        }

        container.innerHTML = filteredTransfers.map(transfer => this.createTransferHTML(transfer)).join('');
    }

    createTransferHTML(transfer) {
        const transferClass = transfer.type === 'in' ? 'transfer-in' : 'transfer-out';
        const typeClass = transfer.type === 'in' ? 'in' : 'out';
        const typeText = transfer.type === 'in' ? 'Przyjście' : 'Odejście';

        return `
            <article class="transfer-entry ${transferClass}">
                <div class="transfer-header">
                    <h3 class="player-name">${transfer.playerName}</h3>
                    <span class="transfer-type ${typeClass}">${typeText}</span>
                </div>
                
                <div class="transfer-details">
                    <div class="detail-item">
                        <span class="detail-label">Z:</span>
                        <span class="detail-value">${transfer.fromTeam}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Do:</span>
                        <span class="detail-value">${transfer.toTeam}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Data:</span>
                        <span class="detail-value">${this.formatDate(transfer.transferDate)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Opłata:</span>
                        <span class="detail-value">${transfer.fee}</span>
                    </div>
                </div>
                
                <div class="transfer-summary">
                    ${transfer.summary}
                </div>
                
                <div class="transfer-source">
                    <a href="${transfer.sourceUrl}" target="_blank" class="source-link">
                        📄 Źródło: ${transfer.sourceName}
                    </a>
                </div>
            </article>
        `;
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pl-PL', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }

    showError(message) {
        const container = document.getElementById('transfers-container');
        container.innerHTML = `<div class="error">${message}</div>`;
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new EkstraklasaTransfers();
});