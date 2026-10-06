from dataclasses import dataclass
@dataclass
class Provider:
    id:int
    name:str
    active:bool=True
