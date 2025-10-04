# Knowledge Graph Dashboard

A modern React dashboard for the Enterprise Knowledge Graph & Ontology Platform. Built with Vite, React Router, and Tailwind CSS.

## Features

- **Dashboard Overview** - Statistics and metrics visualization
- **SPARQL Query Interface** - Interactive query editor with syntax highlighting
- **GDPR Compliance Monitoring** - Track consents, DSR requests, and compliance status
- **Data Quality Metrics** - SHACL validation statistics and quality dimensions
- **Ontology Explorer** - Browse OWL classes and properties

## Tech Stack

- **React 18** - UI library
- **Vite** - Fast build tool
- **TailwindCSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Recharts** - Data visualization
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

```bash
cd dashboard
npm install
```

### Development

```bash
npm run dev
```

The dashboard will be available at http://localhost:3000

### Build for Production

```bash
npm run build
npm run preview
```

## API Integration

The dashboard connects to the FastAPI backend at `http://localhost:8000/api/v1`. Make sure the API server is running:

```bash
# In the project root
source venv/bin/activate
python src/api/server.py
```

## Project Structure

```
dashboard/
├── src/
│   ├── components/     # Reusable UI components
│   │   └── Layout.jsx  # Main layout with navigation
│   ├── pages/          # Page components
│   │   ├── Dashboard.jsx
│   │   ├── SPARQLQuery.jsx
│   │   ├── Compliance.jsx
│   │   ├── DataQuality.jsx
│   │   └── Ontologies.jsx
│   ├── services/       # API service layer
│   │   └── api.js
│   ├── App.jsx         # Root component with routing
│   ├── main.jsx        # Application entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML template
├── vite.config.js      # Vite configuration
├── tailwind.config.js  # Tailwind configuration
└── package.json        # Dependencies
```

## Available Pages

### 1. Dashboard (`/dashboard`)
- Knowledge graph statistics
- Property distribution charts
- System health monitoring
- Quick action links

### 2. SPARQL Query (`/sparql`)
- Interactive SPARQL editor
- Example queries
- Results table view
- JSON export functionality

### 3. Compliance (`/compliance`)
- Consent status distribution
- DSR request monitoring
- Overdue request alerts
- Expiring consents tracking

### 4. Data Quality (`/data-quality`)
- Quality score overview
- 6 quality dimensions
- SHACL statistics
- Validation metrics

### 5. Ontologies (`/ontologies`)
- Browse OWL classes
- Explore object and data properties
- Search functionality
- Namespace information

## Customization

### Styling

The dashboard uses Tailwind CSS. Customize colors in `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Your custom colors
      },
    },
  },
}
```

### API Endpoint

Update the API base URL in `src/services/api.js` or `vite.config.js` proxy settings.

## License

Part of the Enterprise Knowledge Graph & Ontology Platform project.
