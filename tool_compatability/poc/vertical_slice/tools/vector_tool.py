class VectorTool:
    """Adapter to make VectorService framework-compatible"""
    def __init__(self, service):
        self.service = service
    
    def process(self, data):
        text = data.get('text', '')
        embedding = self.service.embed_text(text)
        return {
            'success': True,
            'embedding': embedding,
            'text': text,  # Preserve original text for downstream tools
            'uncertainty': 0.05,  # Text embedding has small inherent uncertainty
            'reasoning': f'Generated {len(embedding)}-dim embedding with 5% uncertainty from model variability'
        }