import numpy as np
import cv2
import time

class Ball:
    """
    Simulates a size 7 Basket ball(75cm circumference ~12cm radius) under gravity, bouncing off the walls of the window.
    All units: position in px (cm), velocity in px/s (cm/s), acceleration in px/s^2 (cm/s^2), timestep dt (s).
    All colisions are perfectly elastic by default i.e. there are no losses. chnage coeff_of_restitution for realistic simulation.
    computes timestep dt for state update, in seconds, based on the fps required (currently set to 60).  
    """
    def __init__(self, radius=12, window_width=640, window_height=480, gravity=980):
        self.radius = radius
        self.w = window_width
        self.h = window_height
        self.gravity = gravity
        self.pos = np.array([self.w / 2, self.h / 2], dtype=float)
        self.vel = np.array([0.0, 0.0], dtype=float)

    def update(self, dt):
        
        self.vel[1] += self.gravity * dt
        self.pos += self.vel * dt

    def draw(self, frame):
        center = (int(round(self.pos[0])), int(round(self.pos[1])))
        cv2.circle(frame, center, self.radius, (0, 120, 255), -1)

def run_simulation():
    width, height = 640, 480
    fps = 60
    dt = 1.0 / fps

    ball = Ball(radius=12, window_width=width, window_height=height, gravity=980)

    while True:
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        ball.update(dt)
        ball.draw(frame)
        cv2.imshow("Ball", frame)
        key = cv2.waitKey(int(dt * 1000)) & 0xFF
        if key == 27:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_simulation()
