from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.messages.flat.QuickChatSelection import QuickChatSelection
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util import offense
from util.ball_prediction_analysis import find_slice_at_time
from util.car import Car
from util.field import Field
from util.game_info import GameInfo
from util.sequence import Sequence, ControlStep
from util.vec import Vec3


class MyBot(BaseAgent):

    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.active_sequence: Sequence = None
        self.field: Field = None
        self.car: Car = None

    def initialize_agent(self):
        self.field = Field(self.get_field_info(), self.team)
        self.car = Car(self.index)

    def update(self, packet: GameTickPacket):
        self.field.update(packet)
        self.car.update(packet)

    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        if self.active_sequence and not self.active_sequence.done:
            controls = self.active_sequence.tick(packet)
            if controls is not None:
                return controls
        
        self.update(packet)
        self.active_sequence = self.assess_position(packet)
        return self.active_sequence.tick(packet)

    def assess_position(self, packet: GameTickPacket) -> Sequence:
        gi = GameInfo(packet=packet, car=self.car, field=self.field, bot=self)
        if gi.packet.game_info.is_kickoff_pause:
            return offense.kickoff(gi)
        
        return offense.push_ball_toward_target(gi, Vec3(self.field.opponent_goal.location))
        # return offense.follow_ball_on_ground(gi)
