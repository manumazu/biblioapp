import pytest, json
from biblioapp import create_app


def test_base_route():
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
    	response = test_client.get('/')
    	assert response.status_code == 200
    	assert b"localisation d'objets" in response.data

#/api/module/YmlidXMwMDAx/
'''def test_module_route():
    flask_app = create_app()
    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
    	response = test_client.get('/api/module/YmlidXMwMDAx/')
    	json_output = json.dumps(response.data.decode('utf-8'))
    	assert "arduino_name" in json_output
    	assert response.status_code == 200
'''