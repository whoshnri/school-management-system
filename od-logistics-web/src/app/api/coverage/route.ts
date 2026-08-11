import { NextResponse } from "next/server";

import {
  deriveCoverageStatus,
  distanceToBoundaryKm,
  distanceToNearestEdgeKm,
  getCoverageBoundaryFromEnv,
  getOutlierThresholdFromEnv,
  haversineDistanceKm,
  isPointInBoundary,
  normalizeUkPostcode,
} from "@/lib/coverage";
import type { Coordinates, CoverageResponse } from "@/lib/coverage-types";

type ProviderName = "postcodes.io" | "google" | "nominatim";
type SecondaryProviderName = "google" | "nominatim";

interface GeocodeResult<TProvider extends ProviderName = ProviderName> {
  provider: TProvider;
  point: Coordinates;
}

interface CoverageRequestBody {
  postcode?: string;
}

export async function POST(request: Request) {
  let body: CoverageRequestBody;

  try {
    body = (await request.json()) as CoverageRequestBody;
  } catch {
    return NextResponse.json({ error: "Invalid JSON body." }, { status: 400 });
  }

  const rawPostcode = body.postcode?.trim() ?? "";
  const normalizedPostcode = normalizeUkPostcode(rawPostcode);

  if (!normalizedPostcode) {
    return NextResponse.json(
      { error: "Please provide a valid UK postcode." },
      { status: 400 },
    );
  }

  const boundary = getCoverageBoundaryFromEnv();
  const outlierThresholdKm = getOutlierThresholdFromEnv();

  const primary = await geocodeWithPostcodesIo(normalizedPostcode);
  const secondary = await geocodeWithSecondaryProvider(normalizedPostcode);

  if (!primary && !secondary) {
    return NextResponse.json(
      {
        error:
          "We couldn't resolve that postcode at the moment. Please try again or request a custom quote.",
      },
      { status: 502 },
    );
  }

  const resolved = resolveCoordinate(primary, secondary, outlierThresholdKm);
  const inCoverage = isPointInBoundary(resolved.point, boundary);
  const boundaryDistance = distanceToBoundaryKm(resolved.point, boundary);
  const nearestEdgeDistance = distanceToNearestEdgeKm(resolved.point, boundary);
  const status = deriveCoverageStatus(inCoverage, nearestEdgeDistance, outlierThresholdKm);

  const response: CoverageResponse = {
    inputPostcode: rawPostcode,
    normalizedPostcode,
    point: resolved.point,
    boundary,
    inCoverage,
    status,
    distanceToBoundaryKm: roundTo3(boundaryDistance),
    distanceToNearestEdgeKm: roundTo3(nearestEdgeDistance),
    outlierThresholdKm,
    diagnostics: {
      primaryProvider: "postcodes.io",
      secondaryProvider: secondary?.provider ?? null,
      secondaryDistanceKm: roundNullable(resolved.secondaryDistanceKm),
      ignoredSecondary: resolved.ignoredSecondary,
      resolvedWith: resolved.resolvedWith,
    },
  };

  return NextResponse.json(response);
}

async function geocodeWithPostcodesIo(postcode: string): Promise<GeocodeResult | null> {
  try {
    const url = `https://api.postcodes.io/postcodes/${encodeURIComponent(postcode)}`;
    const response = await fetch(url, { cache: "no-store" });

    if (!response.ok) {
      return null;
    }

    const payload = (await response.json()) as {
      result?: { latitude?: number; longitude?: number };
    };

    const lat = payload.result?.latitude;
    const lng = payload.result?.longitude;

    if (typeof lat !== "number" || typeof lng !== "number") {
      return null;
    }

    return { provider: "postcodes.io", point: { lat, lng } };
  } catch {
    return null;
  }
}

async function geocodeWithSecondaryProvider(
  postcode: string,
): Promise<GeocodeResult<SecondaryProviderName> | null> {
  const googleApiKey = process.env.GOOGLE_GEOCODING_API_KEY?.trim();

  if (googleApiKey) {
    const googleResult = await geocodeWithGoogle(postcode, googleApiKey);
    if (googleResult) {
      return googleResult;
    }
  }

  return geocodeWithNominatim(postcode);
}

async function geocodeWithGoogle(
  postcode: string,
  apiKey: string,
): Promise<GeocodeResult<"google"> | null> {
  try {
    const params = new URLSearchParams({
      components: `postal_code:${postcode}|country:GB`,
      key: apiKey,
    });

    const response = await fetch(
      `https://maps.googleapis.com/maps/api/geocode/json?${params.toString()}`,
      { cache: "no-store" },
    );

    if (!response.ok) {
      return null;
    }

    const payload = (await response.json()) as {
      status?: string;
      results?: Array<{ geometry?: { location?: { lat?: number; lng?: number } } }>;
    };

    if (payload.status !== "OK" || !payload.results?.length) {
      return null;
    }

    const location = payload.results[0]?.geometry?.location;
    const lat = location?.lat;
    const lng = location?.lng;

    if (typeof lat !== "number" || typeof lng !== "number") {
      return null;
    }

    return { provider: "google", point: { lat, lng } };
  } catch {
    return null;
  }
}

async function geocodeWithNominatim(
  postcode: string,
): Promise<GeocodeResult<"nominatim"> | null> {
  try {
    const params = new URLSearchParams({
      postalcode: postcode,
      countrycodes: "gb",
      format: "jsonv2",
      limit: "1",
    });

    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?${params.toString()}`,
      {
        cache: "no-store",
        headers: {
          "User-Agent":
            process.env.NOMINATIM_USER_AGENT ?? "od-logistics-web/0.1 (cloud-agent)",
        },
      },
    );

    if (!response.ok) {
      return null;
    }

    const payload = (await response.json()) as Array<{ lat?: string; lon?: string }>;
    if (!payload.length) {
      return null;
    }

    const lat = Number.parseFloat(payload[0].lat ?? "");
    const lng = Number.parseFloat(payload[0].lon ?? "");

    if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
      return null;
    }

    return { provider: "nominatim", point: { lat, lng } };
  } catch {
    return null;
  }
}

function resolveCoordinate(
  primary: GeocodeResult | null,
  secondary: GeocodeResult<SecondaryProviderName> | null,
  outlierThresholdKm: number,
): {
  point: Coordinates;
  ignoredSecondary: boolean;
  secondaryDistanceKm: number | null;
  resolvedWith: "primary" | "secondary" | "blended";
} {
  if (!primary && secondary) {
    return {
      point: secondary.point,
      ignoredSecondary: false,
      secondaryDistanceKm: null,
      resolvedWith: "secondary",
    };
  }

  if (!primary) {
    throw new Error("Primary geocode result is missing.");
  }

  if (!secondary) {
    return {
      point: primary.point,
      ignoredSecondary: false,
      secondaryDistanceKm: null,
      resolvedWith: "primary",
    };
  }

  const separationKm = haversineDistanceKm(primary.point, secondary.point);

  if (separationKm > outlierThresholdKm) {
    return {
      point: primary.point,
      ignoredSecondary: true,
      secondaryDistanceKm: separationKm,
      resolvedWith: "primary",
    };
  }

  return {
    point: {
      lat: (primary.point.lat + secondary.point.lat) / 2,
      lng: (primary.point.lng + secondary.point.lng) / 2,
    },
    ignoredSecondary: false,
    secondaryDistanceKm: separationKm,
    resolvedWith: "blended",
  };
}

function roundTo3(value: number): number {
  return Math.round(value * 1000) / 1000;
}

function roundNullable(value: number | null): number | null {
  return value === null ? null : roundTo3(value);
}
