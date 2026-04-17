# Sunrise & Sunset — Year View

An interactive, zero-dependency web app that visualises sunrise, sunset, solar noon, and civil twilight for every day of the year, anywhere on Earth.

- 🌍 **Works for any location** — use your browser's geolocation or search any city/place via OpenStreetMap
- 🕒 **Timezone-aware** — looks up the correct IANA zone (including DST rules) for the selected coordinates
- 🌓 **Polar day / polar night** rendered correctly above the Arctic and Antarctic circles
- ☀️ / 🌙 **Light and dark modes** that follow your system preference
- 📊 **Two views** — full clock chart of sunrise/sunset, or a daylight-hours length curve
- ℹ️ **Built-in explainers** for every term (civil twilight, solar noon, etc.)

## How it works

All computation happens client-side. Sun positions are calculated with the [NOAA solar position algorithm](https://gml.noaa.gov/grad/solcalc/calcdetails.html), ported to vanilla JavaScript. Location search uses [OpenStreetMap Nominatim](https://nominatim.org/) and timezone lookups use [timeapi.io](https://timeapi.io).

No frameworks, no build step — a single `index.html` file.

## Run locally

```bash
# Any static server works, e.g.:
python3 -m http.server 8000
# then open http://localhost:8000
```

## Files

- `index.html` — the whole app (HTML, CSS, SVG chart, solar math)
- `gen.py` — original Python prototype of the NOAA algorithm (not used at runtime; kept for reference)

## License

MIT — see [LICENSE](LICENSE).

---

Made by [Jon H. Øistad](https://github.com/joistad).
