"""Compute sunrise/sunset and related solar times for Oslo for every day of 2026.
Uses NOAA solar position algorithm. Outputs JSON for the page.
"""
import math, json, datetime as dt

# Oslo, Ellingsrudåsen approx
LAT = 59.9139
LON = 10.7522
TZ_OFFSET_STD = 1    # CET
# Europe/Oslo: DST starts last Sunday March, ends last Sunday October

def last_sunday(year, month):
    # find last Sunday of month
    d = dt.date(year, month, 28)
    # go to end of month
    next_month = (d.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
    last_day = next_month - dt.timedelta(days=1)
    # weekday: Monday=0 ... Sunday=6
    offset = (last_day.weekday() - 6) % 7
    return last_day - dt.timedelta(days=offset)

def is_dst(date, year):
    start = last_sunday(year, 3)
    end = last_sunday(year, 10)
    return start <= date < end

def solar_event(date, lat, lon, event):
    """Return UTC decimal hours for 'sunrise' or 'sunset' or 'solar_noon' or 'civil_dawn'/'civil_dusk'.
    NOAA algorithm.
    """
    # Julian day
    y = date.year; m = date.month; d = date.day
    if m <= 2:
        y -= 1; m += 12
    A = y // 100
    B = 2 - A + A // 4
    JD = int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + B - 1524.5
    # For noon we want JD at 0 UT; fine.
    # fractional day default 0 (we iterate but analytic form is fine)
    # Julian century
    T = (JD - 2451545.0) / 36525.0

    # Geometric mean longitude of sun (deg)
    L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360
    # Mean anomaly
    M = 357.52911 + T * (35999.05029 - 0.0001537 * T)
    # Eccentricity
    e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T)
    # Sun's equation of center
    Mrad = math.radians(M)
    C = (math.sin(Mrad) * (1.914602 - T * (0.004817 + 0.000014 * T))
         + math.sin(2 * Mrad) * (0.019993 - 0.000101 * T)
         + math.sin(3 * Mrad) * 0.000289)
    # True longitude
    true_long = L0 + C
    # Apparent longitude
    omega = 125.04 - 1934.136 * T
    lam = true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))
    # Obliquity
    seconds = 21.448 - T * (46.8150 + T * (0.00059 - T * 0.001813))
    eps0 = 23 + (26 + (seconds / 60)) / 60
    eps = eps0 + 0.00256 * math.cos(math.radians(omega))
    # Declination
    decl = math.degrees(math.asin(math.sin(math.radians(eps)) * math.sin(math.radians(lam))))
    # Equation of time (minutes)
    y_ = math.tan(math.radians(eps / 2)) ** 2
    eot = 4 * math.degrees(
        y_ * math.sin(2 * math.radians(L0))
        - 2 * e * math.sin(Mrad)
        + 4 * e * y_ * math.sin(Mrad) * math.cos(2 * math.radians(L0))
        - 0.5 * y_ * y_ * math.sin(4 * math.radians(L0))
        - 1.25 * e * e * math.sin(2 * Mrad)
    )

    # Hour angle for given altitude
    if event in ("sunrise", "sunset"):
        h = -0.833  # refraction + solar disc
    elif event in ("civil_dawn", "civil_dusk"):
        h = -6
    elif event == "solar_noon":
        h = None
    else:
        raise ValueError(event)

    # Solar noon in UT minutes
    solar_noon_ut = (720 - 4 * lon - eot)  # minutes UTC

    if h is None:
        return solar_noon_ut / 60.0

    cos_ha = ((math.sin(math.radians(h))
               - math.sin(math.radians(lat)) * math.sin(math.radians(decl)))
              / (math.cos(math.radians(lat)) * math.cos(math.radians(decl))))
    if cos_ha > 1:
        return None  # sun never rises
    if cos_ha < -1:
        return None  # sun never sets (polar day) - return None, handle specially
    ha = math.degrees(math.acos(cos_ha))  # degrees

    if event in ("sunrise", "civil_dawn"):
        ut_min = solar_noon_ut - 4 * ha
    else:
        ut_min = solar_noon_ut + 4 * ha
    return ut_min / 60.0  # UT decimal hours

def to_local(decimal_ut, date):
    if decimal_ut is None:
        return None
    offset = 2 if is_dst(date, date.year) else 1
    local = decimal_ut + offset
    # wrap
    local = local % 24
    return local

year = 2026
data = []
start = dt.date(year, 1, 1)
for i in range(365):
    d = start + dt.timedelta(days=i)
    sr = solar_event(d, LAT, LON, "sunrise")
    ss = solar_event(d, LAT, LON, "sunset")
    noon = solar_event(d, LAT, LON, "solar_noon")
    cd = solar_event(d, LAT, LON, "civil_dawn")
    cdu = solar_event(d, LAT, LON, "civil_dusk")
    rec = {
        "date": d.isoformat(),
        "sunrise": to_local(sr, d),
        "sunset": to_local(ss, d),
        "noon": to_local(noon, d),
        "civil_dawn": to_local(cd, d),
        "civil_dusk": to_local(cdu, d),
        "daylight": (ss - sr) if (sr is not None and ss is not None) else None,
        "dst": is_dst(d, d.year),
    }
    data.append(rec)

with open("/home/user/workspace/sun-oslo/data.json", "w") as f:
    json.dump({"lat": LAT, "lon": LON, "location": "Oslo, Norway", "year": year, "days": data}, f)

# quick sanity print
print("Jan 1:", data[0])
print("Jun 21:", data[171])
print("Dec 21:", data[354])
