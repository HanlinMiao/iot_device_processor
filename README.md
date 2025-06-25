# IoT Device Processor

A Django REST API application for processing IoT device payloads with token authentication, duplicate detection, and status tracking.

## Features

- **Token Authentication**: Secure API endpoints with Django REST Framework token authentication
- **Device Management**: Automatic device creation and status tracking
- **Payload Processing**:
  - Base64 to Hexadecimal conversion
  - Duplicate detection using fCnt (frame counter)
  - Status determination (passing/failing based on data value)

## Quick Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd iot_device_processor
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Start Development Server
```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## API Usage

### Authentication

First, obtain an authentication token:

```bash
# Create a token for your user via Django admin at http://localhost:8000/admin/
# Or use Django shell:
python manage.py shell
```

```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user = User.objects.get(username='your_username')
token, created = Token.objects.get_or_create(user=user)
print(f"Your token: {token.key}")
```

### API Endpoints

#### 1. Submit IoT Payload
```bash
POST /api/v1/payloads/
Authorization: Token your_token_here
Content-Type: application/json

{
    "fCnt": 100,
    "devEUI": "abcdabcdabcdabcd",
    "data": "AQ==",
    "rxInfo": [
        {
            "gatewayID": "1234123412341234",
            "name": "G1",
            "time": "2022-07-19T11:00:00",
            "rssi": -57,
            "loRaSNR": 10
        }
    ],
    "txInfo": {
        "frequency": 86810000,
        "dr": 5
    }
}
```

#### 2. List All Devices
```bash
GET /api/v1/devices/
Authorization: Token your_token_here
```

#### 3. Get Device Details
```bash
GET /api/v1/devices/<deviceEUI>/
Authorization: Token your_token_here
```

#### 4. List Payloads
```bash
GET /api/v1/payloads/list/
Authorization: Token your_token_here

# Filter by device
GET /api/v1/payloads/list/?devEUI=<deviceEUI>
```

## Data Processing Logic

1. **Device Creation**: Devices are automatically created when first payload is received
2. **Duplicate Detection**: Uses `fCnt` field to prevent duplicate payloads per device
3. **Base64 to Hex**: Converts base64 `data` field to hexadecimal representation
4. **Status Logic**:
   - If hex value equals 1 → "passing"
   - Any other value → "failing"
5. **Device Status Update**: Each device tracks its latest status from most recent payload
