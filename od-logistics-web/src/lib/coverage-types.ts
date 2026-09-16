export type CoverageStatus = "inside" | "near-boundary" | "outside";

export interface CoverageBoundary {
  minLat: number;
  maxLat: number;
  minLng: number;
  maxLng: number;
}

export interface Coordinates {
  lat: number;
  lng: number;
}

export interface GeocodeDiagnostics {
  primaryProvider: "postcodes.io";
  secondaryProvider: "google" | "nominatim" | null;
  secondaryDistanceKm: number | null;
  ignoredSecondary: boolean;
  resolvedWith: "primary" | "secondary" | "blended";
}

export interface CoverageResponse {
  inputPostcode: string;
  normalizedPostcode: string;
  point: Coordinates;
  boundary: CoverageBoundary;
  inCoverage: boolean;
  status: CoverageStatus;
  distanceToBoundaryKm: number;
  distanceToNearestEdgeKm: number;
  outlierThresholdKm: number;
  diagnostics: GeocodeDiagnostics;
}
