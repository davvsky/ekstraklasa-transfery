# Ekstraklasa Transfery

A web application for tracking transfers in and out of the Polish Ekstraklasa football league.

## Features

- 📱 **Responsive Design** - Works on desktop and mobile devices
- 🔍 **Filter System** - Filter transfers by team and type (in/out)
- 📰 **Journal Style** - Transfers displayed as news entries with summaries
- 🔗 **Source Links** - Each transfer includes source URL for verification
- ⚡ **Fast Loading** - Static HTML/CSS/JS for quick performance

## Live Demo

Access the application at: `https://[your-username].github.io/ekstraklasa-transfery/`

## Project Structure

```
├── index.html          # Main application file
├── simple.html         # Standalone version with embedded data
├── styles.css          # Responsive styling
├── script.js           # Original version (requires API server)
├── api_server.py       # Python API server (for development)
├── scraper.py          # Web scraper for real-time data
└── README.md           # This file
```

## Usage

### Quick Start
Open `simple.html` in your browser - it contains sample transfer data and works immediately.

### Development Mode
1. Start the API server:
   ```bash
   python3 api_server.py
   ```
2. Open `http://localhost:8080` in your browser

### Data Sources
The scraper is designed to collect data from:
- 90minut.pl
- Transfermarkt.pl  
- Ekstraklasa.org
- Official club websites

## Deployment

This project is optimized for GitHub Pages deployment:

1. Push to GitHub
2. Enable GitHub Pages in repository settings
3. Select source as "main" branch
4. Access at the provided URL

## Technologies Used

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Python 3 (optional API server)
- **Scraping**: BeautifulSoup, Requests
- **Hosting**: GitHub Pages (free)

## Future Improvements

- [ ] Automated data updates via GitHub Actions
- [ ] Real-time transfer notifications
- [ ] Historical transfer database
- [ ] Transfer value analytics
- [ ] Club comparison tools

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this project for your own purposes.