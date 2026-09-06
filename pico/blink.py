from machine import Pin
from utime import sleep

pin = Pin("LED", Pin.OUT)

#Test program to check Pico works
def toggle_a_few():
    for i in range(3):
        pin.toggle()
        sleep(1)
        print(f"going through loop {i}")

try:
    toggle_a_few()
except KeyboardInterrupt:
    print("caught it")

pin.off()
print("done")
