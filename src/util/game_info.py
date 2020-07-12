from dataclasses import dataclass

from rlbot.agents.base_agent import BaseAgent
from rlbot.utils.structures.game_data_struct import GameTickPacket

from util.car import Car
from util.field import Field


@dataclass
class GameInfo:
    packet: GameTickPacket
    car: Car
    field: Field
    bot: BaseAgent
