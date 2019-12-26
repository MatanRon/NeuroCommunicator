"""Module for connecting to Sphero and using data from API to control it"""

from spheropy.Sphero import Sphero
from time import sleep
import random
from threading import Thread


class NeuroSphero:
    """
    A class that receives data from Neurosteers's Api, sets up connection to the Sphero ball
    and gives orders to the ball upon processed data.

    Args:
        sphero id: user's sphero
        features: the biomarkers on which the user want perform analysis
     """

    def __init__(self, sphero_id):
        self.sphero_ball = Sphero("NAME", sphero_id, response_time_out=2, number_tries=5)
        self.sample_number = 1
        self.y_prediction = -1

        return

    def connect(self):
        try:
            print("connecting to sphero ball...")
            self.sphero_ball.connect()
            self.sphero_ball.set_color(255, 255, 255)
        except ValueError:
            print("Could not connect to sphero ball")
            print("please make sure sphero is on and bluetooth is on")
            return False

        return True

    def make_a_step(self, current_angle, speed, sleep_time):
        self.sphero_ball.roll(speed, current_angle)
        sleep(sleep_time)
        self.sphero_ball.roll(0, current_angle)

    def make_a_square(self):
        speed = 0x30
        sleep_time = 1
        for _ in range(5):
            for angle in [1, 90, 180, 270]:
                self.sphero_ball.roll(speed, angle)
                sleep(sleep_time)
            self.sphero_ball.roll(0, 0)

    def make_a_circle(self, steps=8):
        speed = 0x30
        sleep_time = 0.3
        rotate_by = 360 // steps
        current_angle = 1
        for _ in range(2):
            for _ in range(steps):
                self.make_a_step(current_angle % 360, speed, sleep_time)
                current_angle += rotate_by


    def colorFade(self, colorFrom, colorTo, wait_ms=4, steps=50):
        step_R = (colorTo[0] - colorFrom[0]) / steps
        step_G = (colorTo[1] - colorFrom[1]) / steps
        step_B = (colorTo[2] - colorFrom[2]) / steps
        r = colorFrom[0]
        g = colorFrom[1]
        b = colorFrom[2]

        for x in range(steps):
            self.sphero_ball.set_color(int(r), int(g), int(b))
            sleep(wait_ms / 1000.0)
            r += step_R
            g += step_G
            b += step_B

    def blink(self, wait_ms=5, steps=50):
        c1 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.colorFade((255, 255, 255), (c1[0], c1[1], c1[2]), wait_ms=wait_ms, steps=steps)
        for _ in range(4):
            c2 = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.colorFade((c1[0], c1[1], c1[2]), (c2[0], c2[1], c2[2]), wait_ms=wait_ms, steps=steps)
            c1 = c2

    def control_sphero(self):
        while True:
            y = self.y_prediction  # pull prediction from main thread

            if y == 0:  # Memory game
                print('Memory game')
                for _ in range(3):
                    self.colorFade((149, 0, 179), (0, 0, 255), 20)
                    self.colorFade((0, 0, 255), (0, 200, 200), 20)
                    self.colorFade((0, 200, 200), (149, 0, 179), 20)

            if y == 1:  # Meditate
                print('Meditate')
                for _ in range(3):
                    self.colorFade((0, 25, 0), (0, 255, 0))
                    self.colorFade((0, 255, 0), (0, 25, 0))

            if y == 2:  # Write with weak hand
                print('Write with weak hand')
                for _ in range(3):
                    self.colorFade((255, 128, 0), (255, 200, 0), 20)
                    self.colorFade((255, 200, 0), (230, 0, 0), 20)
                    self.colorFade((230, 0, 0), (255, 128, 0), 20)


            if y == 3:  # Happy music (dancing)
                print('Happy music')
                self.thread_circle = Thread(target=self.make_a_circle)
                self.thread_circle.start()
                self.blink()
                self.thread_circle.join()

            if y == -1:  # No prediction\uncertain
                for _ in range(3):
                    self.sphero_ball.set_color(255, 255, 255)
                    sleep(0.5)

            if y == -2:  # connection error
                for _ in range(4):
                    self.colorFade((50, 0, 0), (255, 0, 0))
                    self.colorFade((255, 0, 0), (50, 0, 0))

            if y == -3:  # training mode
                for _ in range(4):
                    self.colorFade((50, 50, 50), (255, 255, 255))
                    self.colorFade((255, 255, 255), (50, 50, 50))
