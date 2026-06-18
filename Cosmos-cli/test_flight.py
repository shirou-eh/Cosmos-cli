import sys
from cosmos.config import state
from cosmos.data import PARTS
from cosmos.vab import Rocket
from cosmos.flight import FlightSession

rocket = Rocket("Test")
rocket.add_part("pods", "pod_1", "center")
rocket.add_part("tanks", "tank_1", "center")
rocket.add_part("engines", "eng_2", "center")

flight = FlightSession(rocket, "Terra")
flight.state = "FLIGHT"
flight.throttle = 100

for i in range(10):
    flight.tick(0.1)
    print(f"Alt: {flight.altitude:.3f}, Vel: {flight.velocity:.3f}, Mass: {flight.rocket.get_total_mass()}")
