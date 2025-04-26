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
        # Starting position and velocity 
        self.pos = np.array([self.w / 2, self.h / 2], dtype=float) 
        self.vel = np.array([1000.0, 1000.0], dtype=float)

    def update(self, dt, coeff_of_restitution=1.0):
        """
        update position and velocity over timestep dt,
        applying gravity and bouncing off the walls.
        """
        self.vel[1] += self.gravity * dt
        self.pos += self.vel * dt

        # check for collision with top/bottom walls
        if self.pos[1] - self.radius < 0:
            self.pos[1] = self.radius
            self.vel[1] *= -coeff_of_restitution
        elif self.pos[1] + self.radius > self.h:
            self.pos[1] = self.h - self.radius
            self.vel[1] *= -coeff_of_restitution
        
        # check for collision with left/right walls
        if self.pos[0] - self.radius < 0:
            self.pos[0] = self.radius
            self.vel[0] *= -coeff_of_restitution
        elif self.pos[0] + self.radius > self.w:
            self.pos[0] = self.w - self.radius
            self.vel[0] *= -coeff_of_restitution

    def draw(self, frame):
        """
        Render the ball on the frame.
        """
        center = (int(round(self.pos[0])), int(round(self.pos[1])))
        cv2.circle(frame, center, self.radius, (0, 120, 255), -1)

def run_simulation():
    # Env Setup
    width, height = 640, 480
    fps = 60
    frame_interval = 1.0 / fps
    ball = Ball(radius=12, window_width=width, window_height=height, gravity=980)
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    prev_time = time.perf_counter()

    while True:
        loop_start = time.perf_counter()
         #elapsed time since last physics update
        dt = loop_start - prev_time
        dt = min(frame_interval, dt) # in case of compute lag, cap to avoid errorous behavious
        
        frame.fill(0) # Reset Env for new frame
        ball.update(dt, coeff_of_restitution=0.98)
        prev_time = loop_start
        ball.draw(frame)
        cv2.imshow("Ball", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # hit ESC to quit
            break

        loop_end = time.perf_counter()
        elapsed_sim_time = loop_end - loop_start
        sleep_time = frame_interval - elapsed_sim_time
        if sleep_time > 0:
            time.sleep(sleep_time)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_simulation()
