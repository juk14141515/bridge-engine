class RuntimeRouter:
    def route(self, session_state):
        completion = session_state.get('completion_rate', 0)

        if completion == 0:
            return 'reduce_friction'

        if completion < 50:
            return 'guided_support'

        if completion < 100:
            return 'momentum_building'

        return 'completion_export'
