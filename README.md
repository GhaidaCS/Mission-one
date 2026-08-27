# PX4 Mission

Flies a small square mission in PX4 SITL. While it flies, a watchdog
keeps an eye on the battery, if it drops below 20%, the mission gets
cancelled and the drone heads home instead of finishing the route.

## Running it

Set your home position before starting SITL:

```bash
export PX4_HOME_LAT=24.8540475
export PX4_HOME_LON=46.7129178
make px4_sitl jmavsim
```

Then run the script:

```bash
python3 px4_mission.py
```

## How it works

`run_mission()` and `watchdog()` run at the same time. Whoever finishes
first decides what happens, mission done means land normally, low
battery means pause, cancel, and return to launch.
