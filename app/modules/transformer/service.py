class TransformerService:
    def __init__(self, payload, rule):
        self.payload = payload
        self.rule = rule

    def transformPayload(self):
        return self.payload
