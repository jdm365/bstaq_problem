import curses
from time import sleep, perf_counter_ns
import math

def ELEVATOR(floor: int):
    elevator = [
        "╔═════════╗",
        "║  Floor  ║",
        "║" + (5 - len(str(floor))) * " " + str(floor) + "    ║",
        "║    O    ║",
        "║   \\|/   ║",
        "║    |    ║",
        "║   / \\   ║",
        "╚═════════╝",
    ]
    return elevator

ELEVATOR_FLOOR = "|---------|"
ELEVATOR_SHAFT = "|         |"

CLOUD = [
    "   .--.   ",
    "  (    )  ",
    "(        )",
    " \\--__--/  ",
    ]


class ElevatorState:
    def __init__(self, standard_screen: object, num_floors: int = 10_000):
        ## Let y be floor height * current floor
        self.current_y    = 0.0
        self.floor_height = 20

        self.target_floor = 0
        self.num_floors = num_floors
        self.speed = 0.5
        self.travel_distance = 0.0

        self.standard_screen = standard_screen
        self.screen_height, self.screen_width = standard_screen.getmaxyx()
        self.standard_screen.keypad(True)
        self.standard_screen.clear()

    @property
    def current_floor(self):
        return int(self.current_y) // self.floor_height


    def handle_floor_selection(self):
        h, w = 5, 20 
        y = self.screen_height // 2 - h // 2
        x = self.screen_width  // 2 - w // 2

        win = curses.newwin(h, w, y, x)
        win.box()

        prompt = f"Floor 1-{self.num_floors}:"
        win.addstr(1, 1, prompt)
        win.refresh()

        curses.echo()
        curses.curs_set(1)

        inp = win.getstr(2, 1, len(str(self.num_floors)))
        curses.noecho()
        curses.curs_set(0)

        try:
            floor = int(inp.decode("utf-8"))
            if 1 <= floor <= self.num_floors:
                self.target_floor = floor - 1
                self.speed     = 0.5
                self.travel_distance = abs(
                    self.target_floor - self.current_floor
                ) * self.floor_height
        except ValueError:
            pass

        win.clear()
        self.standard_screen.touchwin()
        self.standard_screen.refresh()
    
    def handle_input(self):
        ## Not handling multiple keys at once
        key = self.standard_screen.getch()

        if key == curses.KEY_UP:
            if self.speed == 0.0:
                self.target_floor = min(self.current_floor + 1, self.num_floors - 1)
                self.speed = 0.5

        elif key == curses.KEY_DOWN:
            if self.speed == 0.0:
                self.target_floor = max(self.current_floor - 1, 0)
                self.speed = 0.5

        elif key == ord(' '):
            self.handle_floor_selection()

        elif key == ord('s'):
            self.travel_distance = 0.0
            self.target_floor = self.current_floor
            self.speed = 0.25

        else:
            pass

    def update(self):
        target_y = self.target_floor * self.floor_height

        distance_remaining = abs(target_y - self.current_y)
        relative_distance_remaining = (
                distance_remaining / self.travel_distance 
                if self.travel_distance > 0 
                else 0
                )

        if self.travel_distance != 0:
            if relative_distance_remaining < 0.5:
                self.speed -= 0.05 * (math.log10(self.travel_distance))
            else:
                self.speed += 0.05 * (math.log10(self.travel_distance))

            self.speed = max(0.1, self.speed)

        if self.current_y < target_y:
            ## Going up
            self.current_y = min(self.current_y + self.speed, target_y)

        elif self.current_y > target_y:
            ## Going down 
            self.current_y = max(self.current_y - self.speed, target_y)

        if self.current_y == target_y:
            self.speed = 0
            self.travel_distance = 0.0


    def render(self):
        self.standard_screen.erase()

        ## Render metadata
        self.standard_screen.addstr(
            0, 
            0, 
            f"Current Height:    {self.current_y:.1f}m\n"
            f"Current Floor:     {self.current_floor+1}/{self.num_floors}\n"
            f"Target Floor:      {self.target_floor+1}/{self.num_floors}\n"
            "Select Floor:      <SPACE>\n"
            "Emergency Stop:    <s>\n"
            "Up/Down One Floor: <UP>/<DOWN>\n"
            "Quit:              <CTRL + C>\n"
        )

        elevator_list = ELEVATOR(self.current_floor + 1)

        ## Render ground
        if self.current_y >= -self.screen_height // 2:
            screen_y_ground = (self.screen_height // 2) + int(self.current_y)
            screen_y_ground += len(elevator_list) - 1

            if screen_y_ground < self.screen_height - 1:
                self.standard_screen.addstr(
                    screen_y_ground,
                    0,
                    self.screen_width * "-",
                )


        ## Render elevator
        x_pos = self.screen_width // 2
        y_offset = int(self.current_y)

        for screen_y in range(self.screen_height):
            world_y = screen_y - y_offset
            if world_y > len(elevator_list) + (self.screen_height // 2) - 2:
                break

            if world_y % self.floor_height == 0:
                if world_y < len(elevator_list) + (self.screen_height // 2) - 2:
                    self.standard_screen.addstr(screen_y, x_pos, ELEVATOR_FLOOR)
            else:
                self.standard_screen.addstr(screen_y, x_pos, ELEVATOR_SHAFT)

        for idx, _str in enumerate(elevator_list):
            y = idx + self.screen_height // 2
            x = self.screen_width // 2

            self.standard_screen.addstr(y, x, _str)

        ## Render clouds
        cloud_left_y  = (self.current_y // 150) * 150
        cloud_left_x  = self.screen_width // 4
        cloud_left_maybe_on_screen = (
                (cloud_left_y - self.current_y <= self.screen_height // 2)
                    or
                (self.current_y - cloud_left_y >= self.screen_height // 2)
                )
        if cloud_left_maybe_on_screen:
            for idx, _str in enumerate(CLOUD):
                screen_y = int(self.current_y - cloud_left_y) + idx

                if screen_y < 0 or screen_y >= self.screen_height:
                    continue

                self.standard_screen.addstr(screen_y, cloud_left_x, _str)

        cloud_right_y = ((self.current_y // 200) * 200) + 50
        cloud_right_x = 3 * self.screen_width // 4
        cloud_right_maybe_on_screen = (
                (cloud_right_y - self.current_y <= self.screen_height // 2)
                    or
                (self.current_y - cloud_right_y >= self.screen_height // 2)
                )
        if cloud_right_maybe_on_screen:
            for idx, _str in enumerate(CLOUD):
                screen_y = int(self.current_y - cloud_right_y) + idx

                if screen_y < 0 or screen_y >= self.screen_height:
                    continue

                self.standard_screen.addstr(screen_y, cloud_right_x, _str)

        self.standard_screen.noutrefresh()
        curses.doupdate()


    def main_loop(self):
        tick_speed_ms = 30
        while True:
            start_time = perf_counter_ns()

            self.handle_input()
            self.update()
            self.render()

            time_taken_ms = (perf_counter_ns() - start_time) // 1_000_000
            time_remaining_ms = tick_speed_ms - time_taken_ms

            sleep(max(0, time_remaining_ms / 1000))


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.clear()

    elevator = ElevatorState(stdscr)
    elevator.main_loop()

if __name__ == '__main__':
    curses.wrapper(main)
