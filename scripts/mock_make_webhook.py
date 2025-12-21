#!/usr/bin/env python3
"""
Mock Make.com webhook receiver for local testing.

This simple Flask server simulates Make.com's webhook endpoint.
It validates HMAC signatures and logs received payloads.

Usage:
    python scripts/mock_make_webhook.py

Then configure your .env:
    MAKE_WEBHOOK_URL=http://localhost:8001/webhook
    MAKE_WEBHOOK_SECRET=test-secret-key
"""
import json
import hmac
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

# Secret key for HMAC validation (should match MAKE_WEBHOOK_SECRET in .env)
SECRET_KEY = 'test-secret-key'


def verify_signature(body, signature_header):
    """Verify HMAC signature from webhook."""
    if not signature_header:
        return False
    
    # Expected format: "sha256=<hex_digest>"
    if not signature_header.startswith('sha256='):
        return False
    
    received_signature = signature_header[7:]  # Remove "sha256=" prefix
    
    # Compute expected signature
    expected_signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(received_signature, expected_signature)


@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive webhook POST request."""
    print("\n" + "="*80)
    print("📨 Received Webhook")
    print("="*80)
    
    # Get headers
    content_type = request.headers.get('Content-Type')
    idempotency_key = request.headers.get('Idempotency-Key')
    signature = request.headers.get('X-Make-Signature')
    
    print(f"Content-Type: {content_type}")
    print(f"Idempotency-Key: {idempotency_key}")
    print(f"X-Make-Signature: {signature}")
    
    # Get body
    body = request.get_data()
    
    # Verify signature
    if signature:
        if verify_signature(body, signature):
            print("✅ Signature verified successfully")
        else:
            print("❌ Signature verification FAILED")
            return jsonify({'error': 'Invalid signature'}), 401
    else:
        print("⚠️  No signature provided")
    
    # Parse and display payload
    try:
        payload = json.loads(body)
        print("\n📋 Payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        
        # Extract key information
        print(f"\n📌 Summary:")
        print(f"   Appointment ID: {payload.get('appointment_id')}")
        print(f"   Event Type: {payload.get('event_type')}")
        print(f"   Customer: {payload.get('customer', {}).get('first_name')} {payload.get('customer', {}).get('last_name')}")
        print(f"   Salon: {payload.get('salon', {}).get('name')}")
        print(f"   Stylist: {payload.get('stylist', {}).get('name')}")
        print(f"   Services: {', '.join([s['name'] for s in payload.get('services', [])])}")
        print(f"   Total: {payload.get('total_price')} تومان")
        print(f"   Date/Time: {payload.get('appointment_start')}")
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return jsonify({'error': 'Invalid JSON'}), 400
    
    print("="*80 + "\n")
    
    # Return success
    return jsonify({
        'success': True,
        'message': 'Webhook received successfully',
        'idempotency_key': idempotency_key
    }), 200


@app.route('/webhook/fail', methods=['POST'])
def webhook_fail():
    """Test endpoint that always returns 500 (for testing retries)."""
    print("⚠️  Simulating server error (500)")
    return jsonify({'error': 'Simulated server error'}), 500


@app.route('/', methods=['GET'])
def index():
    """Info page."""
    return """
    <html>
    <head><title>Mock Make.com Webhook Server</title></head>
    <body style="font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px;">
        <h1>🔗 Mock Make.com Webhook Server</h1>
        <p>This server simulates Make.com's webhook endpoint for local testing.</p>
        
        <h2>Endpoints:</h2>
        <ul>
            <li><code>POST /webhook</code> - Main webhook endpoint (returns 200)</li>
            <li><code>POST /webhook/fail</code> - Test endpoint (always returns 500)</li>
        </ul>
        
        <h2>Configuration:</h2>
        <p>Set these environment variables in your <code>.env</code> file:</p>
        <pre style="background: #f0f0f0; padding: 15px; border-radius: 5px;">
MAKE_WEBHOOK_URL=http://localhost:8001/webhook
MAKE_WEBHOOK_SECRET=test-secret-key
        </pre>
        
        <h2>Testing:</h2>
        <p>Create an appointment via the Django app, and the webhook will be sent here.</p>
        <p>Check the terminal where this script is running to see webhook details.</p>
        
        <h3>Manual Test with curl:</h3>
        <pre style="background: #f0f0f0; padding: 15px; border-radius: 5px; overflow-x: auto;">
curl -X POST http://localhost:8001/webhook \\
  -H "Content-Type: application/json" \\
  -H "Idempotency-Key: test-key-123" \\
  -H "X-Make-Signature: sha256=$(echo -n '{"test":"data"}' | openssl dgst -sha256 -hmac 'test-secret-key' | cut -d' ' -f2)" \\
  -d '{"test":"data"}'
        </pre>
    </body>
    </html>
    """


if __name__ == '__main__':
    print("🚀 Starting Mock Make.com Webhook Server...")
    print(f"📡 Listening on http://localhost:8001")
    print(f"🔑 Secret Key: {SECRET_KEY}")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=8001, debug=True)
