from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class SoilLayer(BaseModel):
    depth_start: float = Field(..., description="Start depth in meters")
    depth_end: float = Field(..., description="End depth in meters")
    soil_type: str = Field(..., description="Soil classification (e.g., clay, sand)")
    strength: Optional[float] = Field(None, description="Shear strength in kPa")

class ProjectInfo(BaseModel):
    location: str = Field(..., description="Project location")
    client: Optional[str] = Field(None, description="Client name, optional")
    date: Optional[str] = Field(None, description="Report date")

class HazardInfo(BaseModel):
    erosion: Optional[str] = Field(None, description="Erosion hazard status")
    slide: Optional[str] = Field(None, description="Slide hazard status")
    seismic: Optional[str] = Field(None, description="Seismic hazard status")
    steep_slope: Optional[str] = Field(None, description="Steep slope hazard status")
    watercourse_buffer: Optional[str] = Field(None, description="Watercourse buffer status")

class DocumentSummary(BaseModel):
    doc_type: str = Field(..., description="Type of document (e.g., Soil Report)")
    project_info: ProjectInfo = Field(..., description="Location, client, date")
    soil_profile: List[SoilLayer] = Field(..., description="Soil layers")
    groundwater_depth: Optional[float] = Field(None, description="Depth in meters")
    test_results: Dict[str, float] = Field(..., description="Key test results")
    confidence: str = Field(..., description="High/Medium/Low")
    recommendations: Optional[List[str]] = Field(None, description="List of recommendations")
    hazards: Optional[HazardInfo] = Field(None, description="Hazard information")
    slope_angle: Optional[float] = Field(None, description="Slope angle in degrees")
    lake_proximity: Optional[float] = Field(None, description="Distance to lake in meters")

class Report(BaseModel):
    report_type: str = Field(..., description="Type of report")
    executive_summary: str = Field(..., description="Summary of findings")
    site_description: str = Field(..., description="Site details")
    methodology: str = Field(..., description="Investigation methods")
    findings: str = Field(..., description="Detailed findings")
    recommendations: str = Field(..., description="Engineering recommendations")