import asyncio
from mavsdk import System
from mavsdk.telemetry import LandedState
from mavsdk.mission import MissionItem, MissionPlan

async def position(drone: System):
    async for pos in drone.telemetry.position():
        print(f"posision {pos}") #call it in main using asyncio.create_task(pos(drone))
        await asyncio.sleep(1)

async def battery(drone: System):
    async for battery in drone.telemetry.battery():
        print(f"battery: {battery.remaining_percent}")
        await asyncio.sleep(1)

async def in_air(drone:System):
    async for in_air in drone.telemetry.in_air():
        print(in_air)
        await asyncio.sleep(1)

async def check_connection(drone: System):
    async for connection in drone.core.connection_state():
        print(f"is the drone connected: {connection.is_connected}")
        if connection.is_connected:
            print("drone connected")
            break

async def watchdog(drone: System):
    BATTERY_THREASHOLD = 20
    async for battery in drone.telemetry.battery():
        if battery.remaining_percent < BATTERY_THREASHOLD:
            return

async def run_mission(drone: System, mission_plan):
    await drone.mission.upload_mission(mission_plan)
    print("mission uploaded")

    await drone.mission.start_mission()

    async for mission_progress in drone.mission.mission_progress():
        if mission_progress.current == mission_progress.total:
            break

async def run():
    drone = System()

    await drone.connect(system_address="udp://:14540")
    print("Drone connected")

    asyncio.create_task(position(drone))
    asyncio.create_task(battery(drone))
    asyncio.create_task(in_air(drone))

    await check_connection(drone)

    absolute_latitude = 24.8540475
    absolute_longitude = 46.7129178

    await drone.action.arm()

    async for armed in drone.telemetry.armed(): #we removed the sleep with this loop since sleep is not practical
        if armed:
            print("Drone armed")
            break

    await drone.action.takeoff()
    async for state in drone.telemetry.landed_state():
        if state == LandedState.IN_AIR:
            print("Drone take off")
            break

    mission_items = []

    mission_items.append(MissionItem(absolute_latitude - 10 * 1e-5,
                                     absolute_longitude - 10 * 1e-5,
                                     5,
                                     5,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.VehicleAction.NONE))

    mission_items.append(MissionItem(absolute_latitude + 10 * 1e-5,
                                     absolute_longitude - 10 * 1e-5,
                                     5,
                                     5,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.VehicleAction.NONE))

    mission_items.append(MissionItem(absolute_latitude + 10 * 1e-5,
                                     absolute_longitude + 10 * 1e-5,
                                     5,
                                     5,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.VehicleAction.NONE))
    
    mission_items.append(MissionItem(absolute_latitude - 10 * 1e-5,
                                     absolute_longitude + 10 * 1e-5,
                                     5,
                                     5,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.VehicleAction.NONE))

    mission_items.append(MissionItem(absolute_latitude - 10 * 1e-5,
                                     absolute_longitude - 10 * 1e-5,
                                     5,
                                     5,
                                     True,
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.CameraAction.NONE,
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     float('nan'),
                                     MissionItem.VehicleAction.NONE))

    mission_plan = MissionPlan(mission_items)

    watchdog_task = asyncio.create_task(watchdog(drone))
    mission_task = asyncio.create_task(run_mission(drone, mission_plan))


    done, pending = await asyncio.wait({watchdog_task, mission_task}, return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()

    if mission_task in done:
        await drone.action.land()
        async for landed in drone.telemetry.landed_state():
            if landed == LandedState.ON_GROUND:
                print("Drone landed")
                break
    elif watchdog_task in done:
        print("Low battery")
        await drone.mission.pause_mission()
        mission_task.cancel()
        await drone.action.return_to_launch()
        async for landed in drone.telemetry.landed_state():
            if landed == LandedState.ON_GROUND:
                print("Drone landed")
                break

asyncio.run(run())
