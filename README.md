# Contract Intelligence Parser

A comprehensive contract intelligence system for accounts receivable SaaS platforms. This system automatically processes contracts, extracts critical financial and operational data, and provides confidence scores with gap analysis.

## 🚀 Features

### Core Functionality
- **Automated Contract Processing**: Upload PDF contracts for automatic data extraction
- **Real-time Status Tracking**: Monitor processing progress with live updates
- **Intelligent Data Extraction**: Extract parties, financial details, payment terms, and SLAs
- **Confidence Scoring**: 0-100 point weighted scoring system for data reliability
- **Gap Analysis**: Identify missing information and get actionable recommendations
- **Secure File Handling**: Support for contracts up to 50MB with secure storage

### Technical Capabilities
- **Asynchronous Processing**: Non-blocking uploads with background task processing
- **RESTful API**: Complete REST API with comprehensive endpoints
- **Real-time Updates**: WebSocket-like polling for live status updates
- **Responsive UI**: Modern React interface with drag-and-drop uploads
- **Containerized Deployment**: Full Docker support with docker-compose
- **High Test Coverage**: 60%+ test coverage with comprehensive unit tests

## 🏗️ Architecture

### Backend Stack
- **FastAPI**: High-performance Python web framework
- **MongoDB**: Document database for flexible contract storage
- **Redis**: Task queue backend for Celery
- **Celery**: Distributed task queue for async processing
- **Motor**: Async MongoDB driver
- **PDFPlumber**: Advanced PDF text extraction

### Frontend Stack
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **React Dropzone**: Drag-and-drop file uploads
- **Lucide React**: Beautiful icon library

### Infrastructure
- **Docker**: Containerized services
- **Docker Compose**: Multi-service orchestration
- **MongoDB**: Primary database
- **Redis**: Task queue and caching
- **Celery Flower**: Task monitoring (optional)

## 📊 Data Extraction

The system extracts and structures the following information:

### 1. Party Identification (25 points)
- Contract parties (customer, vendor, third parties)
- Legal entity names and registration details
- Authorized signatories and roles

### 2. Financial Details (30 points)
- Line items with descriptions, quantities, and unit prices
- Total contract value and currency
- Tax information and additional fees

### 3. Payment Structure (20 points)
- Payment terms (Net 30, Net 60, etc.)
- Payment schedules and due dates
- Payment methods and banking details

### 4. Revenue Classification
- Recurring vs. one-time payments
- Subscription models and billing cycles
- Renewal terms and auto-renewal clauses

### 5. Service Level Agreements (15 points)
- Performance metrics and benchmarks
- Penalty clauses and remedies
- Support and maintenance terms

### 6. Account Information (10 points)
- Customer billing details
- Account numbers and references
- Contact information for billing/technical support

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd contract-intelligence-parser
```

### 2. Start with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 3. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Celery Flower**: http://localhost:5555 (optional)

### 4. Development Setup

#### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env

# Start services
uvicorn app.main:app --reload --port 8000

# Start Celery worker (separate terminal)
python start_celery.py
```

#### Frontend Development
```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

## 📡 API Endpoints

### Contract Upload
```http
POST /api/contracts/upload
Content-Type: multipart/form-data

# Response
{
  "contract_id": "uuid",
  "message": "Contract uploaded successfully",
  "status": "pending"
}
```

### Processing Status
```http
GET /api/contracts/{contract_id}/status

# Response
{
  "contract_id": "uuid",
  "status": "processing",
  "progress_percentage": 75,
  "error_message": null
}
```

### Contract Data
```http
GET /api/contracts/{contract_id}

# Response (when completed)
{
  "contract_id": "uuid",
  "filename": "contract.pdf",
  "status": "completed",
  "extracted_data": { ... },
  "confidence_scores": { ... },
  "gap_analysis": { ... }
}
```

### Contract List
```http
GET /api/contracts?page=1&page_size=10&status=completed

# Response
{
  "contracts": [...],
  "total": 50,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

### Contract Download
```http
GET /api/contracts/{contract_id}/download

# Response: PDF file download
```

## 🧪 Testing

### Run Backend Tests
```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run tests with coverage
pytest

# Run specific test file
pytest tests/test_contract_service.py

# Generate coverage report
pytest --cov=app --cov-report=html
```

### Test Coverage
The test suite achieves 60%+ code coverage across:
- Contract service operations
- API endpoint functionality
- Contract parsing logic
- Database operations
- Error handling scenarios

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
MONGODB_URL=mongodb://admin:password123@localhost:27017/contract_parser?authSource=admin
REDIS_URL=redis://localhost:6379/0
DATABASE_NAME=contract_parser
SECRET_KEY=your-secret-key-here
DEBUG=True
```

#### Frontend
```env
VITE_API_BASE_URL=http://localhost:8000/api
```

### Docker Configuration
The system uses Docker Compose with the following services:
- **mongodb**: Database with authentication
- **redis**: Task queue backend
- **backend**: FastAPI application
- **celery_worker**: Background task processor
- **celery_flower**: Task monitoring (optional)

## 📈 Scoring Algorithm

### Weighted Scoring System (0-100 points)
- **Financial completeness**: 30 points
  - Total value (15 pts)
  - Currency (5 pts)
  - Line items (10 pts)

- **Party identification**: 25 points
  - Names (10 pts)
  - Legal entities (8 pts)
  - Signatories (7 pts)

- **Payment terms clarity**: 20 points
  - Payment terms (10 pts)
  - Payment methods (5 pts)
  - Due dates (5 pts)

- **SLA definition**: 15 points
  - Performance metrics (8 pts)
  - Penalty clauses (4 pts)
  - Support terms (3 pts)

- **Contact information**: 10 points
  - Email (5 pts)
  - Phone (3 pts)
  - Account numbers (2 pts)

### Gap Analysis
The system identifies:
- **Missing Fields**: Critical information not found
- **Incomplete Sections**: Partially extracted data
- **Recommendations**: Actionable next steps

## 🔒 Security Features

- **File Type Validation**: Only PDF files accepted
- **File Size Limits**: Maximum 50MB per contract
- **Secure File Storage**: Binary data stored in MongoDB
- **Input Sanitization**: All inputs validated and sanitized
- **Error Handling**: Comprehensive error handling and logging

## 🚀 Deployment

### Production Deployment
```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d

# Scale workers for high load
docker-compose up --scale celery_worker=3
```

### Environment-Specific Configurations
- **Development**: Hot reloading, debug mode, verbose logging
- **Production**: Optimized builds, security headers, monitoring

## 📊 Monitoring

### Application Monitoring
- **Health Checks**: `/health` endpoint for service monitoring
- **Celery Flower**: Task queue monitoring at http://localhost:5555
- **Logging**: Structured logging with different levels
- **Metrics**: Processing times, success rates, error tracking

### Performance Metrics
- **Upload Speed**: Handles 50MB files efficiently
- **Processing Time**: Varies by document complexity
- **Concurrent Processing**: Multiple contracts processed simultaneously
- **Database Performance**: Indexed queries for fast retrieval

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use TypeScript for frontend development
- Write tests for new features
- Update documentation as needed
- Ensure 60%+ test coverage

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
1. Check the [API Documentation](http://localhost:8000/docs)
2. Review the test files for usage examples
3. Check Docker logs: `docker-compose logs -f`
4. Open an issue in the repository

## 🔄 Changelog

### v1.0.0 (Current)
- Initial release with full contract processing pipeline
- React frontend with drag-and-drop uploads
- FastAPI backend with async processing
- MongoDB storage with Redis task queue
- Comprehensive test suite with 60%+ coverage
- Docker containerization with docker-compose
- Real-time status tracking and progress updates
- Advanced PDF parsing with confidence scoring
- Gap analysis and recommendations system

---

**Built with ❤️ for modern contract intelligence and accounts receivable automation.**