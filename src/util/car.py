import math

from rlbot.agents.base_agent import SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.orientation import Orientation, relative_location
from util.sequence import ControlStep, Sequence
from util.vec import Vec3


class Car:
    def __init__(self, car_id: int):
        self.car_id = car_id

        self.location = None
        self.orientation = None
        self.velocity = None
        self.angular_velocity = None
        self.is_demolished = None
        self.has_wheel_contact = None
        self.is_super_sonic = None
        self.is_bot = None
        self.jumped = None
        self.double_jumped = None
        self.name = None
        self.team = None
        self.boost = None
        self.hitbox = None
        self.hitbox_offset = None

    def update(self, packet: GameTickPacket):
        my_car = packet.game_cars[self.car_id]

        self.location = Vec3(my_car.physics.location)
        self.orientation = Orientation(my_car.physics.rotation)
        self.velocity = Vec3(my_car.physics.velocity)
        self.angular_velocity = Vec3(my_car.physics.angular_velocity)
        self.is_demolished = my_car.is_demolished
        self.has_wheel_contact = my_car.has_wheel_contact
        self.is_super_sonic = my_car.is_super_sonic
        self.is_bot = my_car.is_bot
        self.jumped = my_car.jumped
        self.double_jumped = my_car.double_jumped
        self.name = my_car.name
        self.team = my_car.team
        self.boost = my_car.boost
        self.hitbox = my_car.hitbox
        self.hitbox_offset = Vec3(my_car.hitbox_offset)

    def steer_toward_target(self, target: Vec3) -> float:
        current_in_radians = math.atan2(self.orientation.forward.y, -self.orientation.forward.x)
        target_vec = target - self.location
        ideal_in_radians = math.atan2(target_vec.y, -target_vec.x)
        diff = ideal_in_radians - current_in_radians
        if abs(diff) > math.pi:
            if diff < 0:
                diff += 2 * math.pi
            else:
                diff -= 2 * math.pi

        return -1.0 * min(max(round(diff, 2), -1.0), 1.0)

    def front_flip(self, packet) -> Sequence:
        return Sequence([
            ControlStep(duration=0.05, controls=SimpleControllerState(jump=True)),
            ControlStep(duration=0.05, controls=SimpleControllerState(jump=False)),
            ControlStep(duration=0.2, controls=SimpleControllerState(jump=True, pitch=-1)),
            ControlStep(duration=0.8, controls=SimpleControllerState()),
        ])
