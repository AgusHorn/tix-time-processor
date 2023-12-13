class ClockFixer:
    UPSTREAM_SERIALIZATION_TIME = 15 * (10 ** 3)  # 15 micro
    DOWNSTREAM_SERIALIZATION_TIME = 15 * (10 ** 3)  # 15 micro

    def __init__(self, observations, tau):
        self.observations = sorted(observations,
                                   key=lambda o: o.day_timestamp)

    def _between_obs(self, day_timestamp):
        obs = tuple()
        if day_timestamp < self.observations[0].day_timestamp:
            obs = (None, self.observations[0])
        elif self.observations[-1].day_timestamp <= day_timestamp:
            obs = (self.observations[-1], None)
        else:
            for index in range(len(self.observations) - 1):
                if self.observations[index].day_timestamp <= day_timestamp < self.observations[index + 1].day_timestamp:
                    obs = (self.observations[index], self.observations[index + 1])
                    break
        return obs

    def _calculate_observation_phi(self, observation):
        if observation is None:
            return None
        return (observation.initial_timestamp - observation.reception_timestamp +
                ((observation.reception_timestamp - observation.initial_timestamp) +
                 (observation.final_timestamp - observation.sent_timestamp)) / 2)

    def _base_phi_function(self, x):
        obs_before, obs_after = self._between_obs(x)
        phi_before = self._calculate_observation_phi(obs_before)
        phi_after = self._calculate_observation_phi(obs_after)
        slope = 0
        if phi_before is not None and phi_after is not None:
            slope = (phi_before - phi_after) / (obs_before.day_timestamp - obs_after.day_timestamp)
        intercept = 0
        if phi_before is None:
            intercept = phi_after - obs_after.day_timestamp * slope
        else:
            intercept = phi_before - obs_before.day_timestamp * slope
        return x * slope + intercept

    @property
    def phi_function(self):
        return self._base_phi_function