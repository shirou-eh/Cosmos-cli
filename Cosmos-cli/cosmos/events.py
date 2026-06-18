import random

def check_random_event(flight):
    # Микрометеориты только в космосе (высота больше или равна границе атмосферы)
    if flight.altitude > 0 and flight.altitude >= flight.planet["atmosphere"]:
        if random.random() < 0.005: # 0.5% шанс каждый тик
            flight.add_log("Микрометеорит пробил обшивку! Вибрации!", "ALERT")
            flight.add_pitch_wobble(5)
