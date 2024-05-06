from dataclasses import dataclass, field


@dataclass(kw_only=True)
class Security:
    quantity: int | None = None
    risk: int | None = None
    variance: int | None = None
    sd: int | None = None
    history: dict = field(default_factory=dict)

    def __getitem__(self, key):
        return getattr(self, key)
    
    def __setitem__(self, key, value) -> None:
        setattr(self, key, value)


@dataclass
class Stock(Security):
    ticker: str
    sector: str | None = None
    country: str | None = None
    t212_id: str | None = None

    def __init__(self, ticker: str, sector: str | None = None, country: str | None = None, t212_id: str | None = None, **kwargs):
        super().__init__(**kwargs)
        self.ticker = ticker
        self.sector = sector
        self.country = country
        self.t212_id = t212_id       


@dataclass
class Bond(Security):
    # WIP
    pass