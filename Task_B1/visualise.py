"""Task B1.4: the four charts designed in A3.1, drawn from the cleaned SQLite data."""
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statistics

con = sqlite3.connect("airquality.db")

# 1. Trend of PM2.5 over the month (line): daily mean of the whole network and of Adyar
days = con.execute("SELECT day, AVG(pm25) FROM readings GROUP BY day ORDER BY day").fetchall()
adyar = dict(con.execute("SELECT day, AVG(pm25) FROM readings r JOIN stations s USING (station_id) "
                         "WHERE s.name='Adyar' GROUP BY day").fetchall())
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot([int(d[0][-2:]) for d in days], [d[1] for d in days], marker="o", label="All 12 stations")
ax.plot([int(d[0][-2:]) for d in days], [adyar[d[0]] for d in days], marker="s", label="Adyar")
ax.set_xlabel("Day of October 2026"); ax.set_ylabel("Daily mean PM2.5 (ug/m3)")
ax.set_title("Chart 1: PM2.5 trend over October 2026"); ax.legend(); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig("chart1_trend.png", dpi=110); plt.close(fig)
vals = [d[1] for d in days]
print(f"Chart 1: network daily mean ranges {min(vals):.1f} - {max(vals):.1f}, month mean {statistics.mean(vals):.1f}")

# 2. Comparison of stations (bar), sorted
st = con.execute("SELECT s.name, AVG(pm25) FROM readings r JOIN stations s USING (station_id) "
                 "GROUP BY s.name ORDER BY 2 DESC").fetchall()
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar([s[0] for s in st], [s[1] for s in st], color="#4c72b0")
ax.axhline(60, color="red", linestyle="--", label="60 ug/m3 (24-h limit, India NAAQS)")
ax.set_xlabel("Station"); ax.set_ylabel("Mean PM2.5 (ug/m3)"); ax.set_title("Chart 2: mean PM2.5 by station, October 2026")
plt.setp(ax.get_xticklabels(), rotation=45, ha="right"); ax.legend(); fig.tight_layout()
fig.savefig("chart2_stations.png", dpi=110); plt.close(fig)
print("Chart 2: highest", st[0][0], round(st[0][1], 1), "| lowest", st[-1][0], round(st[-1][1], 1),
      "| stations above 60:", sum(1 for s in st if s[1] > 60), "of", len(st))

# 3. Temperature against PM2.5 (scatter) + correlation
pts = con.execute("SELECT temp_c, pm25 FROM readings WHERE temp_c IS NOT NULL AND pm25 IS NOT NULL "
                  "AND filled = 0 AND station_id % 3 = 1").fetchall()
fig, ax = plt.subplots(figsize=(6, 4.5))
ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=6, alpha=0.4)
ax.set_xlabel("Temperature (degrees C)"); ax.set_ylabel("PM2.5 (ug/m3)")
ax.set_title("Chart 3: temperature against PM2.5 (4 stations, measured readings)"); fig.tight_layout()
fig.savefig("chart3_scatter.png", dpi=110); plt.close(fig)
r = statistics.correlation([p[0] for p in pts], [p[1] for p in pts])
print(f"Chart 3: {len(pts)} points, Pearson correlation r = {r:.2f}")

# 4. Hours with the worst air (bar of the mean by hour of day)
hrs = con.execute("SELECT hour, AVG(pm25) FROM readings GROUP BY hour ORDER BY hour").fetchall()
fig, ax = plt.subplots(figsize=(8, 4))
colors = ["#c44e52" if h[1] >= sorted(x[1] for x in hrs)[-3] else "#8da0cb" for h in hrs]
ax.bar([h[0] for h in hrs], [h[1] for h in hrs], color=colors)
ax.set_xlabel("Hour of the day (0-23)"); ax.set_ylabel("Mean PM2.5 (ug/m3)")
ax.set_title("Chart 4: PM2.5 by hour of the day (worst three hours in red)"); fig.tight_layout()
fig.savefig("chart4_hours.png", dpi=110); plt.close(fig)
worst = sorted(hrs, key=lambda h: -h[1])[:3]
best = min(hrs, key=lambda h: h[1])
print("Chart 4: worst hours", [(h[0], round(h[1], 1)) for h in worst], "| best hour", best[0], round(best[1], 1))
con.close()
