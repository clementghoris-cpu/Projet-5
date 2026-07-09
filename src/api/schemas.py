from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class PredictionInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    #OSEBuildingID: int = Field(..., description="ID unique du bâtiment")
    #DataYear: int = Field(..., description="Année de collecte des données")
    BuildingType: str = Field(..., description="Type de bâtiment (ex: Commercial, Residential, etc.)")
    PrimaryPropertyType: str = Field(..., description="Type de propriété principale")
    #PropertyName: str = Field(..., description="Nom de la propriété")
    #Address: str = Field(..., description="Adresse du bâtiment")
    #City: str = Field(..., description="Ville où se trouve le bâtiment")
    #State: str = Field(..., description="État où se trouve le bâtiment")
    #ZipCode: float | None = Field(None, description="Code postal du bâtiment")
    #TaxParcelIdentificationNumber: str = Field(..., description="Numéro d'identification de la parcelle fiscale")
    #CouncilDistrictCode: int | None = Field(None, description="Code du district du conseil")
    Neighborhood: str = Field(..., description="Quartier où se trouve le bâtiment")
    #Latitude: float = Field(..., description="Latitude du bâtiment")
    #Longitude: float = Field(..., description="Longitude du bâtiment")
    YearBuilt: int = Field(..., ge=0, description="Année de construction du bâtiment")
    NumberofBuildings: float | None = Field(None, gt=0, description="Nombre de bâtiments")
    NumberofFloors: int = Field(..., ge=0, description="Nombre de étages")
    #PropertyGFATotal: int = Field(..., description="Surface totale de la propriété")
    PropertyGFAParking: int = Field(..., ge=0, description="Surface de stationnement")
    PropertyGFABuildings: int = Field(..., ge=0, description="Surface totale des bâtiments")
    ListOfAllPropertyUseTypes: str = Field(..., description="Liste de tous les types d'utilisation de la propriété")
    LargestPropertyUseType: str = Field(..., description="Type d'utilisation de la propriété le plus important")
    LargestPropertyUseTypeGFA: float = Field(..., ge=0, description="Surface de la propriété le plus important")
    SecondLargestPropertyUseType: str | None = Field(None, description="Type d'utilisation de la propriété le deuxième plus important")
    SecondLargestPropertyUseTypeGFA: float | None = Field(None, ge=0, description="Surface de la propriété le deuxième plus important")
    ThirdLargestPropertyUseType: str | None = Field(None, description="Type d'utilisation de la propriété le troisième plus important")
    ThirdLargestPropertyUseTypeGFA: float | None = Field(None, ge=0, description="Surface de la propriété le troisième plus important")
    #YearsENERGYSTARCertified: str | None = Field(None, description="Années de certification Energy Star")
    ENERGYSTARScore: float | None = Field(None, ge=0, le=100, description="Score Energy Star")
    steam_use_kbtu: float | None = Field(None, ge=0, description="Utilisation de la vapeur (kBtu)")
    #electricity_kwh: float | None = Field(None, description="Utilisation de l'électricité (kwh)")
    electricity_kbtu: float | None = Field(None, ge=0, description="Utilisation de l'électricité (kBtu)")
    #natural_gas_therms: float | None = Field(None, description="Utilisation du gaz naturel (therms)")
    natural_gas_kbtu: float | None = Field(None, ge=0, description="Utilisation du gaz naturel (kBtu)")
    #DefaultData: bool = Field(..., description="Données par défaut")
    #Comments: float | None = Field(None, description="Commentaires")
    ComplianceStatus: str = Field(..., description="Statut de conformité")
    Outlier: str | None = Field(None, description="Valeur aberrante")
    #TotalGHGEmissions: float | None = Field(None, description="Émissions totales de GES")
    GHGEmissionsIntensity: float | None = Field(None, ge=0, description="Intensité des émissions de GES")

    @field_validator('YearBuilt')
    @classmethod
    def check_year_not_in_future(cls, value: int) -> int:        
        current_year = datetime.now().year
        if value > current_year:
            raise ValueError(f"L'année de construction ne peut pas être dans le futur. Année actuelle: {current_year}")
        return value