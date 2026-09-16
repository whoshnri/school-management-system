# O&D Logistics Coverage Checker

Simple Next.js MVP for UK postcode coverage checks with a visual map:

- UK postcode validation and normalization
- Geocoding via `postcodes.io` (primary), with Google or Nominatim fallback
- Outlier handling: ignore secondary point when it differs by more than 1km (configurable)
- Square boundary coverage check from environment variables
- Visual map with boundary polygon, resolved point tooltip, and 1km radius overlay

## Quick start

1. Install dependencies:

```bash
npm install
```

2. Copy environment config:

```bash
cp .env.example .env.local
```

3. Run development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Environment configuration

The square coverage boundary is configured in `.env.local`:

```bash
COVERAGE_MIN_LAT=51.28
COVERAGE_MAX_LAT=51.70
COVERAGE_MIN_LNG=-0.52
COVERAGE_MAX_LNG=0.33
```

Outlier threshold:

```bash
MAX_GEOCODE_DEVIATION_KM=1
```

Optional provider keys:

```bash
GOOGLE_GEOCODING_API_KEY=
NOMINATIM_USER_AGENT=od-logistics-web/0.1 (your-email@example.com)
```

## API

### `POST /api/coverage`

Request body:

```json
{
  "postcode": "SW1A 1AA"
}
```

Response includes:

- normalized postcode
- resolved point
- square boundary
- in/out coverage status
- distance to boundary and nearest edge
- geocoding diagnostics
