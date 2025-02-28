import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

// Add CORS error handling
const handleCorsError = (event: ErrorEvent) => {
  if (event.message.includes('CORS') || event.message.includes('Failed to fetch')) {
    console.error('CORS Error detected. Make sure your Python backend has CORS enabled.');
    console.info('Add the following to your Python backend:');
    console.info(`
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)  # This enables CORS for all routes
    
    @app.route('/ask', methods=['GET'])
    def ask():
        question = request.args.get('question', '')
        # Your processing logic here
        return jsonify({"answer": "Your response here"})
    
    if __name__ == '__main__':
        app.run(debug=True)
    `);
  }
};

window.addEventListener('error', handleCorsError);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
);