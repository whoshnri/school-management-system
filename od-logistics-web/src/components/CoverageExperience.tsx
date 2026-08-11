"use client";

import dynamic from "next/dynamic";
import { FormEvent, useMemo, useState } from "react";

import type { CoverageBoundary, CoverageResponse, CoverageStatus } from "@/lib/coverage-types";

const CoverageMap = dynamic(() => import("@/components/CoverageMap"), {
  ssr: false,
  loading: () => (
    <div className="h-[420px] w-full animate-pulse rounded-2xl border border-amber-100 bg-amber-50" />
  ),
});

const STATUS_LABEL: Record<CoverageStatus, string> = {
  inside: "Inside coverage",
  "near-boundary": "Near boundary",
  outside: "Outside coverage",
};

const STATUS_CLASS: Record<CoverageStatus, string> = {
  inside: "bg-teal-100 text-teal-900",
  "near-boundary": "bg-amber-100 text-amber-900",
  outside: "bg-red-100 text-red-900",
};

const DEFAULT_BOUNDARY: CoverageBoundary = {
  minLat: parseEnvNumber("NEXT_PUBLIC_COVERAGE_MIN_LAT", 51.28),
  maxLat: parseEnvNumber("NEXT_PUBLIC_COVERAGE_MAX_LAT", 51.7),
  minLng: parseEnvNumber("NEXT_PUBLIC_COVERAGE_MIN_LNG", -0.52),
  maxLng: parseEnvNumber("NEXT_PUBLIC_COVERAGE_MAX_LNG", 0.33),
};

const DEFAULT_MAP_ZOOM = parseEnvNumber("NEXT_PUBLIC_DEFAULT_MAP_ZOOM", 10);

function midpoint(boundary: CoverageBoundary) {
  return {
    lat: (boundary.minLat + boundary.maxLat) / 2,
    lng: (boundary.minLng + boundary.maxLng) / 2,
  };
}

export function CoverageExperience() {
  const [postcode, setPostcode] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CoverageResponse | null>(null);

  const mapBoundary = result?.boundary ?? DEFAULT_BOUNDARY;
  const mapCenter = useMemo(() => midpoint(mapBoundary), [mapBoundary]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/coverage", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ postcode }),
      });

      const payload = (await response.json()) as CoverageResponse | { error?: string };

      if (!response.ok) {
        setResult(null);
        setError(payload.error ?? "Unable to check coverage right now.");
        return;
      }

      setResult(payload as CoverageResponse);
    } catch {
      setResult(null);
      setError("Network error while checking coverage. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:py-12">
      <p className="mb-2 text-center text-sm font-semibold uppercase tracking-[0.2em] text-amber-700">
        Phase 1
      </p>
      <h1 className="mb-8 text-center text-3xl font-bold text-slate-900 sm:text-4xl">
        O&amp;D Logistics Coverage &amp; Quote Checker
      </h1>

      <div className="grid gap-6 lg:grid-cols-[1.25fr_1fr]">
        <section className="rounded-2xl border border-amber-100 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-slate-900">Same-day UK courier</h2>
          <ul className="mt-3 space-y-2 text-sm text-slate-700">
            <li>• Same day delivery</li>
            <li>• Local courier support</li>
            <li>• Business account onboarding</li>
            <li>• Fast &amp; reliable service</li>
          </ul>

          <form className="mt-6 space-y-3" onSubmit={handleSubmit}>
            <label className="block text-sm font-medium text-slate-800" htmlFor="postcode">
              Enter UK postcode to check coverage
            </label>
            <div className="flex flex-col gap-3 sm:flex-row">
              <input
                id="postcode"
                name="postcode"
                type="text"
                required
                placeholder="e.g. SW1A 1AA"
                value={postcode}
                onChange={(event) => setPostcode(event.target.value)}
                className="w-full rounded-xl border border-amber-200 px-4 py-3 text-base uppercase tracking-wide text-slate-900 shadow-sm focus:border-amber-500 focus:outline-none focus:ring-2 focus:ring-amber-200"
              />
              <button
                type="submit"
                disabled={isLoading}
                className="rounded-xl bg-amber-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-amber-700 disabled:cursor-not-allowed disabled:bg-amber-400"
              >
                {isLoading ? "Checking..." : "Check coverage"}
              </button>
            </div>
          </form>

          {error && (
            <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          )}

          {result && (
            <div className="mt-5 space-y-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
              <span
                className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide ${STATUS_CLASS[result.status]}`}
              >
                {STATUS_LABEL[result.status]}
              </span>
              <div className="grid gap-2 text-sm text-slate-700 sm:grid-cols-2">
                <p>
                  <strong>Postcode:</strong> {result.normalizedPostcode}
                </p>
                <p>
                  <strong>Resolved point:</strong> {result.point.lat.toFixed(5)},{" "}
                  {result.point.lng.toFixed(5)}
                </p>
                <p>
                  <strong>Distance to boundary:</strong> {result.distanceToBoundaryKm} km
                </p>
                <p>
                  <strong>Distance to nearest edge:</strong> {result.distanceToNearestEdgeKm} km
                </p>
                <p>
                  <strong>Outlier threshold:</strong> {result.outlierThresholdKm} km
                </p>
                <p>
                  <strong>Secondary outlier ignored:</strong>{" "}
                  {result.diagnostics.ignoredSecondary ? "Yes" : "No"}
                </p>
              </div>

              <p className="text-sm text-slate-700">
                {result.inCoverage
                  ? "Great news — this postcode is currently covered. Request your quote below."
                  : "This postcode is outside the default coverage square. You can still request a custom quote."}
              </p>
            </div>
          )}

          <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm">
            <h3 className="font-semibold text-slate-900">Get a quote</h3>
            <p className="mt-2 text-slate-700">
              Contact us directly for immediate pricing or custom routes.
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <a
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 font-medium text-slate-800 hover:bg-slate-100"
                href="mailto:quotes@odlogistics.co.uk"
              >
                Email
              </a>
              <a
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 font-medium text-slate-800 hover:bg-slate-100"
                href="https://wa.me/447700900123"
                target="_blank"
                rel="noreferrer"
              >
                WhatsApp
              </a>
              <a
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 font-medium text-slate-800 hover:bg-slate-100"
                href="tel:+447700900123"
              >
                Call
              </a>
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-amber-100 bg-white p-4 shadow-sm">
          <h2 className="mb-3 text-lg font-semibold text-slate-900">Coverage visual map</h2>
          <CoverageMap
            boundary={mapBoundary}
            result={result}
            defaultCenter={mapCenter}
            defaultZoom={DEFAULT_MAP_ZOOM}
          />
          <p className="mt-3 text-xs text-slate-600">
            Square boundary is your configured service area. The dashed 1km circle around the
            postcode point shows the max deviation threshold.
          </p>
        </section>
      </div>
    </div>
  );
}

function parseEnvNumber(name: string, fallback: number): number {
  const raw = process.env[name];
  if (!raw) {
    return fallback;
  }

  const parsed = Number.parseFloat(raw);
  return Number.isFinite(parsed) ? parsed : fallback;
}
