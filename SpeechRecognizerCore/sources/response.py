class Response:
    def __init__(self,
                 status: int,
                 body: dict):
        self.status = status
        self.body = body

    def to_dict(self):
        return {
            "status": self.status,
            "body": self.body
        }
