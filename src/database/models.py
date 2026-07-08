from sqlalchemy import Boolean, Column, Float, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class TrainData(Base):
    __tablename__ = "train_data"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    OSEBuildingID = Column(Integer, nullable=False)
    DataYear = Column(Integer, nullable=False)
    BuildingType = Column(String, nullable=False)
    PrimaryPropertyType = Column(String, nullable=False)
    PropertyName = Column(String, nullable=False)
    Address = Column(String, nullable=False)
    City = Column(String, nullable=False)
    State = Column(String, nullable=False)
    ZipCode = Column(Float, nullable=True)
    TaxParcelIdentificationNumber = Column(String, nullable=False)
    CouncilDistrictCode = Column(Integer, nullable=True)
    Neighborhood = Column(String, nullable=False)
    Latitude = Column(Float, nullable=False)
    Longitude = Column(Float, nullable=False)
    YearBuilt = Column(Integer, nullable=False)
    NumberofBuildings = Column(Float, nullable=True)
    NumberofFloors = Column(Integer, nullable=False)
    PropertyGFATotal = Column(Integer, nullable=False)
    PropertyGFAParking = Column(Integer, nullable=True)
    property_gfa_buildings = Column(Integer, nullable=True)
    ListOfAllPropertyUseTypes = Column(String, nullable=False)
    LargestPropertyUseType = Column(String, nullable=False)
    LargestPropertyUseTypeGFA = Column(Float, nullable=False)
    SecondLargestPropertyUseType = Column(String, nullable=True)
    SecondLargestPropertyUseTypeGFA = Column(Float, nullable=True)
    ThirdLargestPropertyUseType = Column(String, nullable=True)
    ThirdLargestPropertyUseTypeGFA = Column(Float, nullable=True)
    YearsENERGYSTARCertified = Column(String, nullable=True)
    ENERGYSTARScore = Column(Float, nullable=True)
    steam_use_kbtu = Column(Float, nullable=True)
    electricity_kwh = Column(Float, nullable=True)
    electricity_kbtu = Column(Float, nullable=True)
    natural_gas_therms = Column(Float, nullable=True)
    natural_gas_kbtu = Column(Float, nullable=True)
    DefaultData = Column(Boolean, nullable=False)
    Comments = Column(Float, nullable=True)
    ComplianceStatus = Column(String, nullable=False)
    Outlier = Column(String, nullable=True)
    TotalGHGEmissions = Column(Float, nullable=True)
    GHGEmissionsIntensity = Column(Float, nullable=True)

class PredictionInput(Base):
    __tablename__ = "prediction_input"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    BuildingType = Column(String, nullable=False)
    PrimaryPropertyType = Column(String, nullable=False)
    Neighborhood = Column(String, nullable=False)
    YearBuilt = Column(Integer, nullable=False)
    NumberofBuildings = Column(Float, nullable=True)
    NumberofFloors = Column(Integer, nullable=False)
    PropertyGFAParking = Column(Integer, nullable=True)
    property_gfa_buildings = Column(Integer, nullable=True)
    ListOfAllPropertyUseTypes = Column(String, nullable=False)
    LargestPropertyUseType = Column(String, nullable=False)
    LargestPropertyUseTypeGFA = Column(Float, nullable=False)
    SecondLargestPropertyUseType = Column(String, nullable=True)
    SecondLargestPropertyUseTypeGFA = Column(Float, nullable=True)
    ThirdLargestPropertyUseType = Column(String, nullable=True)
    ThirdLargestPropertyUseTypeGFA = Column(Float, nullable=True)
    ENERGYSTARScore = Column(Float, nullable=True)
    steam_use_kbtu = Column(Float, nullable=True)
    electricity_kbtu = Column(Float, nullable=True)
    natural_gas_kbtu = Column(Float, nullable=True)
    ComplianceStatus = Column(String, nullable=False)
    Outlier = Column(String, nullable=True)
    GHGEmissionsIntensity = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    prediction_output = relationship(
        "PredictionOutput", 
        back_populates="prediction_input",        
        uselist=False,
        cascade="all, delete-orphan"
    )

class PredictionOutput(Base):
    __tablename__ = "prediction_output"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    prediction_input_id = Column(String, ForeignKey("prediction_input.id", ondelete="CASCADE"), nullable=False, unique=True)
    predicted_value = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


    prediction_input = relationship(
        "PredictionInput",
        back_populates="prediction_output"
    )