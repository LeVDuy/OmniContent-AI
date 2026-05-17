import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from Fast_API import app

client = TestClient(app)

def test_health_check():
    """Test if the FastAPI app loads correctly and can handle requests."""
    assert app.title == "Multi-Agent Content Creation API"
    assert app.version == "2.0"

def test_generate_content_missing_fields():
    """Test validation errors for missing required Form fields."""
    response = client.post("/api/generate_content", data={
        "input_type": "topic",
    })
    assert response.status_code == 422 

@pytest.mark.skip(reason="Requires Groq API key and consumes quota")
def test_generate_content_mocked():
    pass
