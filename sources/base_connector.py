from abc import ABC, abstractmethod

class BaseConnector(ABC):
    def __init__(self, source_name):
        super().__init__()  
        self.source_name = source_name
    
    @abstractmethod
    def fetch_data(self):
        pass