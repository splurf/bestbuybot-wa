class Product:
    def __init__(self, sku: str):
        self.sku = sku
        self.model: str = None
        self.name: str = None
        self.url: str = None

    def update(self, sku: str = None, model: str = None, name: str = None, url: str = None):
        """Update any existing information"""

        if sku != None:
            self.sku = sku
        if model != None:
            self.model = model
        if name != None:
            self.name = name
        if url != None:
            self.url = url

    def valid(self) -> bool:
        return (self.url != None) and (self.sku != None) and (self.model != None) and (self.name != None)
