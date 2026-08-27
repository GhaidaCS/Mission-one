# PX4 Mission + Battery Watchdog

Flies a small square mission in PX4 SITL. While it flies, a watchdog
keeps an eye on the battery — if it drops below 20%, the mission gets
cancelled and the drone heads home instead of finishing the route.

## Running it

Set your home position before starting SITL (it defaults to Zurich
otherwise):

```bash
export PX4_HOME_LAT=24.8540475
export PX4_HOME_LON=46.7129178
export PX4_HOME_ALT=600
make px4_sitl gz_x500
```

Then run the script:

```bash
python3 mission.py
```

## How it works

`run_mission()` and `watchdog()` run at the same time. Whoever finishes
first decides what happens — mission done means land normally, low
battery means pause, cancel, and return to launch.

To test the low-battery path, bump `BATTERY_THREASHOLD` up to something
like `0.95` so it trips right away, then set it back to `0.2` for real
runs.

## Notes

- Home position has to be set before SITL starts, via env vars — QGC
  can't change it, it just shows whatever the sim already picked.
- If positions look off after changing home, restart SITL fresh.
