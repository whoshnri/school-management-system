"use client";

import { useEffect, useMemo } from "react";
import {
  Circle,
  CircleMarker,
  MapContainer,
  Polygon,
  TileLayer,
  Tooltip,
  useMap,
} from "react-leaflet";
import type { LatLngBoundsExpression, LatLngExpression } from "leaflet";
import "leaflet/dist/leaflet.css";

import type {
  Coordinates,
  CoverageBoundary,
  CoverageResponse,
  CoverageStatus,
} from "@/lib/coverage-types";

const STATUS_COLOR: Record<CoverageStatus, string> = {
  inside: "#0f766e",
  "near-boundary": "#b45309",
  outside: "#b91c1c",
};

interface CoverageMapProps {
  boundary: CoverageBoundary;
  result: CoverageResponse | null;
  defaultCenter: Coordinates;
  defaultZoom: number;
}

function MapViewportController({
  bounds,
  point,
}: {
  bounds: LatLngBoundsExpression;
  point: Coordinates | null;
}) {
  const map = useMap();

  useEffect(() => {
    if (point) {
      map.flyTo([point.lat, point.lng], Math.max(map.getZoom(), 11), {
        duration: 0.75,
      });
      return;
    }

    map.fitBounds(bounds, { padding: [30, 30] });
  }, [bounds, map, point]);

  return null;
}

export default function CoverageMap({
  boundary,
  result,
  defaultCenter,
  defaultZoom,
}: CoverageMapProps) {
  const bounds = useMemo<LatLngBoundsExpression>(
    () => [
      [boundary.minLat, boundary.minLng],
      [boundary.maxLat, boundary.maxLng],
    ],
    [boundary],
  );

  const squareCoordinates = useMemo<LatLngExpression[]>(
    () => [
      [boundary.minLat, boundary.minLng],
      [boundary.minLat, boundary.maxLng],
      [boundary.maxLat, boundary.maxLng],
      [boundary.maxLat, boundary.minLng],
    ],
    [boundary],
  );

  const point = result?.point ?? null;
  const pointColor = result ? STATUS_COLOR[result.status] : "#334155";
  const pointResult = point && result ? result : null;

  return (
    <div className="h-[420px] w-full overflow-hidden rounded-2xl border border-amber-100">
      <MapContainer center={[defaultCenter.lat, defaultCenter.lng]} zoom={defaultZoom} className="h-full w-full">
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <MapViewportController bounds={bounds} point={point} />

        <Polygon
          positions={squareCoordinates}
          pathOptions={{ color: "#d97706", weight: 2, fillOpacity: 0.1 }}
        />

        {point && pointResult && (
          <>
            <Circle
              center={[point.lat, point.lng]}
              radius={1000}
              pathOptions={{ color: pointColor, dashArray: "6 6", fillOpacity: 0.08 }}
            />
            <CircleMarker
              center={[point.lat, point.lng]}
              radius={8}
              pathOptions={{ color: pointColor, fillColor: pointColor, fillOpacity: 0.85 }}
            >
              <Tooltip direction="top" offset={[0, -8]} opacity={1} permanent>
                <div className="text-xs">
                  <p className="font-semibold">{pointResult.normalizedPostcode}</p>
                  <p>
                    {point.lat.toFixed(5)}, {point.lng.toFixed(5)}
                  </p>
                  <p className="capitalize">{pointResult.status.replace("-", " ")}</p>
                </div>
              </Tooltip>
            </CircleMarker>
          </>
        )}
      </MapContainer>
    </div>
  );
}
