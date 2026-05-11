class RuntimeSessionState:
    def create(self):
        return {
            'active': True,
            'completion_rate': 0,
            'rewrite_count': 0,
            'friction_level': 'normal',
            'momentum_state': 'starting'
        }
