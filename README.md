# FeedForward

FeedForward is an AI-powered platform for providing formative feedback on student assignments. The system uses multiple AI model runs to generate comprehensive, constructive feedback aligned with rubric criteria.

## Features

- Multiple AI model integration for diverse feedback perspectives
- Configurable number of runs per model for consistency and aggregation
- Instructor-managed assignment creation with custom rubrics
- Student draft submissions with iterative feedback
- Progress tracking across multiple drafts
- Domain-based authentication for institutions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/BARG-Curtin-University/feedforward.git
cd feedforward
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (create a `.env` file):
```
SECRET_KEY=your_secret_key
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_smtp_username
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=no-reply@example.com
APP_DOMAIN=http://localhost:5001
```

5. Initialize the database:
```bash
mkdir -p data
python app/init_db.py
```

6. Run the application:
```bash
python app.py
```

## Development

- Built with FastHTML (based on FastAPI)
- Uses SQLite for database storage
- Tailwind CSS for styling

## License

[MIT License](LICENSE)