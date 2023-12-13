from datetime import datetime, timezone

def observation_rtt_key_function(observation):
    return observation.final_timestamp - observation.initial_timestamp


def upstream_time_function(observation, phi_function):
    return (observation.reception_timestamp + phi_function(observation.day_timestamp)) \
            - observation.initial_timestamp


def downstream_time_function(observation, phi_function):
    return observation.final_timestamp - (observation.sent_timestamp + phi_function(observation.day_timestamp))


def divide_observations_into_minutes(observations):
    observations_per_minute = {}
    for observation in observations:
        observation_datetime = datetime.fromtimestamp(observation.day_timestamp, timezone.utc)
        observation_minute = observation_datetime.replace(second=0, microsecond=0).timestamp()
        if observation_minute not in observations_per_minute:
            observations_per_minute[observation_minute] = []
        observations_per_minute[observation_minute].append(observation)
    return observations_per_minute