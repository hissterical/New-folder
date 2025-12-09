from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # Health check endpoint
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'healthy'}).encode())
            return
        
        # Main endpoint
        if parsed_path.path == '/':
            # Get the question from query parameter
            question = query_params.get('q', [''])[0]
            
            if not question:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'error': 'No question provided',
                    'usage': 'Use /?q=your question here'
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            try:
                # Using Gemini API via curl
                api_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyAw8nHRUe0Dm27A5jkkhFcbPlus1uOfoQw')
                
                if not api_key:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        'error': 'GEMINI_API_KEY not configured',
                        'message': 'Please set GEMINI_API_KEY environment variable'
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Prepare curl command for Gemini API
                curl_command = [
                    'curl',
                    f'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}',
                    '-H', 'Content-Type: application/json',
                    '-d', json.dumps({
                        'contents': [{
                            'parts': [{
                                'text': question
                            }]
                        }]
                    })
                ]
                
                # Execute curl command
                result = subprocess.run(
                    curl_command,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        'error': 'Curl command failed',
                        'details': result.stderr
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Parse the response
                response_data = json.loads(result.stdout)
                
                if 'error' in response_data:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {
                        'error': 'API Error',
                        'details': response_data['error']
                    }
                    self.wfile.write(json.dumps(response).encode())
                    return
                
                # Extract the answer from Gemini response
                answer = response_data['candidates'][0]['content']['parts'][0]['text']
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'question': question,
                    'answer': answer,
                    'model': 'gemini-1.5-flash'
                }
                self.wfile.write(json.dumps(response).encode())
                
            except subprocess.TimeoutExpired:
                self.send_response(504)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'error': 'Request timeout',
                    'message': 'The LLM request took too long'
                }
                self.wfile.write(json.dumps(response).encode())
                
            except json.JSONDecodeError as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'error': 'Failed to parse API response',
                    'details': str(e)
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    'error': 'Internal server error',
                    'details': str(e)
                }
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'error': 'Not found'}
            self.wfile.write(json.dumps(response).encode())
