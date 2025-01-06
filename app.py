import csv
import os
import openai
from flask import Flask, request, jsonify

app = Flask(__name__)
model = 'gpt-4'
client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])


# 2) Load the CSV data into memory (for a small dataset this is fine).
#    For larger datasets, consider a database or a more efficient query strategy.
claims_data = {}
with open('claims.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Store each row in a dictionary keyed by claim_id
        claims_data[row["claim_id"]] = row

@app.route('/claim/<claim_id>', methods=['GET'])
def get_claim_details(claim_id):
    # 3) Retrieve the row matching claim_id
    claim_row = claims_data.get(claim_id)
    
    if not claim_row:
        return jsonify({"error": "Claim ID not found"}), 404
    
    # 4) Prepare a prompt to send to OpenAI
    prompt = f"""
    You are a helpful assistant. Given the insurance claim data below, provide:
    1) A concise summary (in one sentence).
    2) A risk assessment labeled as "low", "medium", or "high".
    
    The data:
    claim_id: {claim_row["claim_id"]}
    policy_holder: {claim_row["policy_holder"]}
    claim_amount: {claim_row["claim_amount"]}
    claim_date: {claim_row["claim_date"]}
    claim_description: {claim_row["claim_description"]}
    
    Return the result as valid JSON with fields "summary" and "risk_assessment".
    """

    # 5) Make a completion call to OpenAI
    try:
        messages = [
            {"role": "system", "content": prompt},
        ]
        response = client.chat.completions.create(model=model, messages=messages)
        # 6) Extract the generated text
        openai_output = response.choices[0].message.content

        # Let's attempt to parse it as JSON if the LLM is well-instructed.
        import json
        ai_json = json.loads(openai_output)
        return jsonify(ai_json), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 7) Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)
