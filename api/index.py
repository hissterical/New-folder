from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def ask_llm():
    # Get the question from query parameter
    question = request.args.get('q', '')
    
    if not question:
        return jsonify({
            'error': 'No question provided',
            'usage': 'Use /?q=your question here'
        }), 400
    
    try:
        # Using Gemini API via curl
        api_key = os.environ.get('GEMINI_API_KEY', '')
        
        if not api_key:
            return jsonify({
                'error': 'GEMINI_API_KEY not configured',
                'message': 'Please set GEMINI_API_KEY environment variable'
            }), 500
        
        # Prepare curl command for Gemini API
        curl_command = [
            'curl',
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}',
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
            return jsonify({
                'error': 'Curl command failed',
                'details': result.stderr
            }), 500
        
        # Parse the response
        # Parse the response
        response_data = json.loads(result.stdout)
        
        if 'error' in response_data:
            return jsonify({
                'error': 'API Error',
                'details': response_data['error']
            }), 500
        
        # Extract the answer from Gemini response
        answer = response_data['candidates'][0]['content']['parts'][0]['text']
        
        return jsonify({
            'question': question,
            'answer': answer,
            'model': 'gemini-pro'
        })
    except subprocess.TimeoutExpired:
        return jsonify({
            'error': 'Request timeout',
            'message': 'The LLM request took too long'
        }), 504
        
    except json.JSONDecodeError as e:
        return jsonify({
            'error': 'Failed to parse API response',
            'details': str(e)
        }), 500
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

# For Vercel
def handler(request):
    with app.request_context(request.environ):
        return app.full_dispatch_request()
