class TableTool:
    """Adapter to make TableService framework-compatible"""
    def __init__(self, service):
        self.service = service
    
    def process(self, data):
        if 'embedding' in data:
            # Try to get original text from data, or use a fallback
            text = data.get('original_text', data.get('text', 'no_text'))
            row_id = self.service.save_embedding(
                text,
                data['embedding']
            )
            return {
                'success': True,
                'row_id': row_id, 
                'uncertainty': 0.0,
                'reasoning': f'Stored embedding with ID {row_id}'
            }
        return {
            'success': False,
            'error': 'No embedding in data',
            'uncertainty': 1.0
        }