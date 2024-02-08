from flask import Flask, request, jsonify, session
from simple_agent_runner import SimpleAgentRunner

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/start', methods=['POST'])
def start_simulation():
    data = request.json
    num_steps = data['num_steps']
    red_agent_type = data['red_agent_type']  # You need to map this to actual class
    session['runner'] = SimpleAgentRunner(num_steps, red_agent_type)
    session['runner'].setup()
    return jsonify({'message': 'Simulation started'})

@app.route('/step', methods=['POST'])
def run_step():
    if 'runner' not in session:
        return jsonify({'error': 'Simulation not started'}), 400

    step_num = request.json.get('step_num', 0)
    state_snapshot = session['runner'].run_step(step_num)
    return jsonify({'state_snapshot': state_snapshot})

@app.route('/reset', methods=['POST'])
def reset_simulation():
    if 'runner' in session:
        session['runner'].reset()
        return jsonify({'message': 'Simulation reset'})
    return jsonify({'error': 'Simulation not started'}), 400

if __name__ == '__main__':
    app.run(debug=True)

