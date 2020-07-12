from rlbot.agents.base_agent import SimpleControllerState

from util.ball_prediction_analysis import find_slice_at_time
from util.debug import Renderer
from util.game_info import GameInfo
from util.sequence import Sequence, SingleStep, ControlStep
from util.vec import Vec3


def go_nuts(gi: GameInfo) -> Sequence:
    ball_location = Vec3(gi.packet.game_ball.physics.location)
    if gi.car.location.flat().dist(ball_location.flat()) > 2000:
        # We're far away from the ball, let's try to lead it a little bit
        ball_prediction = gi.bot.get_ball_prediction_struct()  # This can predict bounces, etc
        ball_in_future_location = Vec3(find_slice_at_time(ball_prediction, gi.packet.game_info.seconds_elapsed + 2).physics.location)
        target_location = ball_in_future_location.flat() + (ball_in_future_location.flat() - Vec3(gi.field.opponent_goal.location)).rescale(2200).flat()
        with Renderer(gi.bot.renderer) as r:
            r.draw_line_3d(ball_location, target_location, r.cyan())
    else:
        target_location = ball_location + (ball_location - Vec3(gi.field.opponent_goal.location)).rescale(100)

    # Draw some things to help understand what the bot is thinking
    with Renderer(gi.bot.renderer) as r:
        r.draw_line_3d(gi.car.location, target_location, r.white())
        r.draw_string_3d(gi.car.location, 1, 1, f'Speed: {gi.car.velocity.length():.1f}', r.white())
        r.draw_rect_3d(target_location, 8, 8, True, r.cyan(), centered=True)

    controls = SimpleControllerState()
    controls.steer = gi.car.steer_toward_target(target_location)
    controls.throttle = 1.0
    controls.boost = abs(controls.steer) < 0.2 and gi.car.velocity.length() < 2000
    # controls.handbrake = abs(controls.steer) > 0.99 and gi.car.location.dist(ball_location) > 1000

    return Sequence([SingleStep(controls)])


def follow_ball_on_ground(gi: GameInfo) -> Sequence:
    ball_loc = Vec3(gi.packet.game_ball.physics.location)
    ball_loc_flat = ball_loc.flat()
    ball_vel_flat = Vec3(gi.packet.game_ball.physics.velocity).flat()
    ball_ground_speed = ball_vel_flat.length()
    ideal_position = ball_loc_flat

    controls = SimpleControllerState(
        steer=gi.car.steer_toward_target(ideal_position)
    )
    car_ground_speed = gi.car.velocity.flat().length()
    car_to_ball_dist = gi.car.location.flat().dist(ball_loc_flat)
    if car_to_ball_dist > 800:
        controls.throttle = 1.0
        controls.boost = abs(controls.steer) < 0.2 and car_ground_speed < 2300
    else:
        if car_ground_speed - ball_ground_speed > 525 and car_to_ball_dist < 500:
            controls.throttle = min(max((ball_ground_speed - car_ground_speed) / 3600, -1.0), 0)
            controls.boost = False
        else:
            controls.throttle = min(max((ball_ground_speed - car_ground_speed) / 525, 0), 1.0)
            controls.boost = ball_ground_speed - car_ground_speed > 992
            if gi.car.location.flat().dist(ball_loc_flat) > 92.75 and ball_loc.z < 200:
                controls.throttle = min(1.0, controls.throttle + 0.1)

    return Sequence([SingleStep(controls)])


def push_ball_toward_target(gi: GameInfo, target: Vec3) -> Sequence:
    ball_loc = Vec3(gi.packet.game_ball.physics.location)
    ball_loc_flat = ball_loc.flat()
    ball_ground_speed = Vec3(gi.packet.game_ball.physics.velocity).flat().length()
    car_to_ball_dist = gi.car.location.flat().dist(ball_loc_flat)
    if ball_ground_speed > 300:
        future_seconds = car_to_ball_dist / 2000.0
        ball_prediction = gi.bot.get_ball_prediction_struct()
        ball_loc_fut_flat = Vec3(find_slice_at_time(ball_prediction, gi.packet.game_info.seconds_elapsed + future_seconds).physics.location).flat()
        ideal_position = ball_loc_fut_flat + (ball_loc_fut_flat - target.flat()).rescale(80)
        # ideal_position = ball_loc_flat + (ball_loc_flat - target.flat()).rescale(80)
    else:
        future_seconds = -1
        ideal_position = ball_loc_flat + (ball_loc_flat - target.flat()).rescale(80)

    with Renderer(gi.bot.renderer) as r:
        r.draw_line_3d(gi.car.location, ideal_position, r.white())
        r.draw_string_3d(gi.car.location, 1, 1, f'Predicted Seconds: {future_seconds:.1f}', r.white())
        r.draw_rect_3d(ideal_position, 8, 8, True, r.cyan(), centered=True)

    controls = SimpleControllerState(
        steer=gi.car.steer_toward_target(ideal_position)
    )
    car_ground_speed = gi.car.velocity.flat().length()
    if ball_loc.z < 150 or car_to_ball_dist > 800:
        if abs(controls.steer) < 0.2:
            controls.throttle = 1.0
            controls.boost = car_ground_speed < 2000
        else:
            controls.throttle = 1.0
            controls.handbrake = gi.car.angular_velocity.length() < 1
    else:
        if car_ground_speed - ball_ground_speed > 525 and car_to_ball_dist < 500:
            controls.throttle = min(max((ball_ground_speed - car_ground_speed) / 3600, -1.0), 0)
            controls.boost = False
        else:
            controls.throttle = min(max((ball_ground_speed - car_ground_speed) / 525, 0), 1.0)
            controls.boost = ball_ground_speed - car_ground_speed > 992 or car_to_ball_dist > 800

    return Sequence([SingleStep(controls)])


def kickoff(gi: GameInfo) -> Sequence:
    with Renderer(gi.bot.renderer) as r:
        r.draw_string_3d(gi.car.location, 1, 1, 'kickoff!', r.white())
    
    ball_location = Vec3(gi.packet.game_ball.physics.location)
    target_location = ball_location + (ball_location - Vec3(gi.field.opponent_goal.location)).rescale(92.75)
    return Sequence([SingleStep(SimpleControllerState(
        steer=gi.car.steer_toward_target(target_location),
        throttle=1.0,
        boost=gi.car.velocity.length() < 2300,
    ))])
