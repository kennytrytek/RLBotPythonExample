from util.boost_pad_tracker import BoostPadTracker

from rlbot.utils.structures.game_data_struct import (
    GameTickPacket, FieldInfoPacket
)


class Field:

    def __init__(self, field: FieldInfoPacket, team: int):
        self.field_info = field

        self.boost_pad_tracker = BoostPadTracker(self.field_info)

        self.my_goal = list(filter(
            lambda g: g.team_num == team, self.field_info.goals
        ))[0]
        self.opponent_goal = list(filter(
            lambda g: g.team_num != team, self.field_info.goals
        ))[0]

    def update(self, game_tick_packet: GameTickPacket):
        self.boost_pad_tracker.update_boost_status(game_tick_packet)
