import logging
import openai
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FactGenerator:
    def __init__(self, config):
        self.config = config
        
        if config.openai_api_key:
            self.client = openai.OpenAI(api_key=config.openai_api_key)
            logger.info("✅ FactGenerator initialized with OpenAI")
        else:
            self.client = None
            logger.warning("⚠️ FactGenerator initialized without OpenAI - will return test data")
    
    def generate_fact(self) -> Dict[str, Any]:
        """
        Generate an interesting fact using OpenAI.
        Falls back to test data if OpenAI is not available.
        """
        if not self.client:
            logger.warning("⚠️ OpenAI not configured, returning test fact")
            return {
                'title': 'Test Fact',
                'content': 'This is a test fact. Configure OPENAI_API_KEY to generate real facts!',
                'category': 'Technology'
            }
        
        try:
            logger.info("🤖 Calling OpenAI to generate fact...")
            
            response = self.client.chat.completions.create(
                model=self.config.openai_model,
                temperature=self.config.openai_temperature,
                max_tokens=self.config.openai_max_tokens,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fact generator that creates interesting, surprising, and educational facts. Return facts in JSON format with 'title', 'content', and 'category' fields. Keep the title under 80 characters and content under 200 characters."
                    },
                    {
                        "role": "user",
                        "content": "Generate a fascinating and little-known fact about science, history, nature, or technology. Make it engaging and surprising!"
                    }
                ]
            )
            
            fact_text = response.choices[0].message.content
            logger.info(f"✅ OpenAI response received: {fact_text[:100]}...")
            
            # Try to parse as JSON, fall back to simple structure
            import json
            try:
                fact_data = json.loads(fact_text)
                if 'title' not in fact_data or 'content' not in fact_data:
                    raise ValueError("Missing required fields")
            except (json.JSONDecodeError, ValueError):
                # If not valid JSON, create structure from text
                logger.info("Converting OpenAI text response to structured format")
                lines = fact_text.strip().split('\n', 1)
                fact_data = {
                    'title': lines[0][:80] if lines else 'Interesting Fact',
                    'content': lines[1][:200] if len(lines) > 1 else fact_text[:200],
                    'category': 'General'
                }
            
            logger.info(f"✅ Fact generated: {fact_data['title']}")
            return fact_data
            
        except Exception as e:
            logger.error(f"❌ Error generating fact with OpenAI: {str(e)}")
            return {
                'title': 'Error Generating Fact',
                'content': f'Failed to generate fact: {str(e)}',
                'category': 'Error'
            }
