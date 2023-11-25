import numpy as np
import math


def sin_values(periods, add):
    values = [math.sin(i/10) * 10 for i in range(periods*20 + add)]
    index = 0
    while True:
        yield values[index]
        index = (index + 1) % len(values)


class controller:
    def __init__(self, pixel_a_coef):
        self.pixel_a_coef = pixel_a_coef
        self.time = 0
        self.M = None
        self.m = None
        self.distance = None
        self.C = None
        self.acoustic = False
        self.time_step = None
        self.k = None
        return

    def set_k(self, k):
        self.k = k

    def set_acoustic(self):
        self.acoustic = True

    def set_optic(self):
        self.acoustic = False

    def update_parameters(self, M, m, distance, K):
        self.M = M
        self.m = m
        self.distance = distance
        self.C = K
        return

    def get_graph(self):
        k_begin = -np.pi / (self.distance * 2)
        k_end = np.pi / (self.distance * 2)
        k = np.linspace(k_begin, k_end, 100)
        first_value = (self.M + self.m) / 2
        second_value = np.sqrt((((self.M - self.m)**2)/4) + (self.M * self.m * (np.cos(k * self.distance)**2)))
        third_value = (2 * self.C) / (self.M * self.m)
        optical_y = third_value * (first_value + second_value)
        acoustic_y = third_value * (first_value - second_value)
        self.previous_optical_w, self.previous_acoustic_w, self.k_range = np.sqrt(optical_y), np.sqrt(acoustic_y), k
        return self.k_range, self.previous_optical_w, self.previous_acoustic_w

    def get_atoms(self, time_step):
        if self.acoustic:
            our_w = self.previous_acoustic_w
        else:
            our_w = self.previous_optical_w
        max_element = self.k_range[self.k_range < self.k].max()
        k_index = np.argmax(self.k_range == max_element)
        w = our_w[k_index]
        if self.acoustic:
            big_atoms = np.cos((2 * self.k * self.distance) - w * self.time)
            small_atoms = big_atoms
            self.time += time_step
            return self.pixel_a_coef * big_atoms, self.pixel_a_coef * small_atoms, k_index / len(self.k_range)
        if self.M > self.m:
            u2 = 1
            u1 = -self.m/self.M
        else:
            u1 = 1
            u2 = -self.M / self.m
        big_atoms = u1 * np.cos((2 * self.k * self.distance) - w * self.time)
        small_atoms = u2 * np.cos((2 * self.k * self.distance) - w * self.time)
        self.time += time_step
        return self.pixel_a_coef * big_atoms, self.pixel_a_coef * small_atoms, k_index / len(self.k_range)
