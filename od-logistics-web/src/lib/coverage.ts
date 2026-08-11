import type { Coordinates, CoverageBoundary, CoverageStatus } from "@/lib/coverage-types";

const UK_POSTCODE_REGEX = /^[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}$/i;

const DEFAULT_BOUNDARY: CoverageBoundary = {
  minLat: 51.28,
  maxLat: 51.7,
  minLng: -0.52,
  maxLng: 0.33,
};

export function normalizeUkPostcode(input: string): string | null {
  const compact = input.replace(/\s+/g, "").toUpperCase();

  if (!UK_POSTCODE_REGEX.test(compact)) {
    return null;
  }

  return `${compact.slice(0, -3)} ${compact.slice(-3)}`;
}

export function getCoverageBoundaryFromEnv(
  env: NodeJS.ProcessEnv = process.env,
): CoverageBoundary {
  const minLat = parseFloatSafe(env.COVERAGE_MIN_LAT, DEFAULT_BOUNDARY.minLat);
  const maxLat = parseFloatSafe(env.COVERAGE_MAX_LAT, DEFAULT_BOUNDARY.maxLat);
  const minLng = parseFloatSafe(env.COVERAGE_MIN_LNG, DEFAULT_BOUNDARY.minLng);
  const maxLng = parseFloatSafe(env.COVERAGE_MAX_LNG, DEFAULT_BOUNDARY.maxLng);

  if (minLat >= maxLat || minLng >= maxLng) {
    return DEFAULT_BOUNDARY;
  }

  return { minLat, maxLat, minLng, maxLng };
}

export function getOutlierThresholdFromEnv(
  env: NodeJS.ProcessEnv = process.env,
): number {
  const value = parseFloatSafe(env.MAX_GEOCODE_DEVIATION_KM, 1);
  return value > 0 ? value : 1;
}

export function isPointInBoundary(
  point: Coordinates,
  boundary: CoverageBoundary,
): boolean {
  return (
    point.lat >= boundary.minLat &&
    point.lat <= boundary.maxLat &&
    point.lng >= boundary.minLng &&
    point.lng <= boundary.maxLng
  );
}

export function distanceToBoundaryKm(
  point: Coordinates,
  boundary: CoverageBoundary,
): number {
  const clampedLat = clamp(point.lat, boundary.minLat, boundary.maxLat);
  const clampedLng = clamp(point.lng, boundary.minLng, boundary.maxLng);

  return haversineDistanceKm(point, { lat: clampedLat, lng: clampedLng });
}

export function distanceToNearestEdgeKm(
  point: Coordinates,
  boundary: CoverageBoundary,
): number {
  if (!isPointInBoundary(point, boundary)) {
    return distanceToBoundaryKm(point, boundary);
  }

  const north = haversineDistanceKm(point, { lat: boundary.maxLat, lng: point.lng });
  const south = haversineDistanceKm(point, { lat: boundary.minLat, lng: point.lng });
  const east = haversineDistanceKm(point, { lat: point.lat, lng: boundary.maxLng });
  const west = haversineDistanceKm(point, { lat: point.lat, lng: boundary.minLng });

  return Math.min(north, south, east, west);
}

export function deriveCoverageStatus(
  inCoverage: boolean,
  distanceToEdgeKm: number,
  nearBoundaryThresholdKm: number,
): CoverageStatus {
  if (!inCoverage) {
    return "outside";
  }

  return distanceToEdgeKm <= nearBoundaryThresholdKm ? "near-boundary" : "inside";
}

export function haversineDistanceKm(a: Coordinates, b: Coordinates): number {
  const earthRadiusKm = 6371;
  const latDelta = degreesToRadians(b.lat - a.lat);
  const lngDelta = degreesToRadians(b.lng - a.lng);
  const lat1 = degreesToRadians(a.lat);
  const lat2 = degreesToRadians(b.lat);

  const sinHalfLat = Math.sin(latDelta / 2);
  const sinHalfLng = Math.sin(lngDelta / 2);

  const h =
    sinHalfLat * sinHalfLat +
    Math.cos(lat1) * Math.cos(lat2) * sinHalfLng * sinHalfLng;

  return 2 * earthRadiusKm * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}

function degreesToRadians(degrees: number): number {
  return (degrees * Math.PI) / 180;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

function parseFloatSafe(input: string | undefined, fallback: number): number {
  if (!input) {
    return fallback;
  }

  const parsed = Number.parseFloat(input);
  return Number.isFinite(parsed) ? parsed : fallback;
}
