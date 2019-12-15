#!/usr/bin/env python3


#  fan_control.py
#  Raspberry Pi fan speed control depending on CPU temperature.
#  Yury Kuznetsov (WFLM)
#  10.12.2019


FAN_GPIO = 4
PWM_FREQUENCY_HZ = 20

TEMP_MAINTAIN = 70
TEMP_CUTOFF = 50

DUTY_LOW_LIMIT = 40
DUTY_HIGH_LIMIT = 100


import time
import pigpio
from simple_pid import PID


class CPUTemperatureSensor:
    def __init__(self):
        cpu_temp_sensor_file_path = "/sys/class/thermal/thermal_zone0/temp"
        self._temp_descriptor = open(cpu_temp_sensor_file_path, mode="rb")

    @property
    def temp(self):
        self._temp_descriptor.seek(0)
        cpu_temperature = self._temp_descriptor.read(6)
        cpu_temperature = float(cpu_temperature) / 1000
        return cpu_temperature

    def __del__(self):
        self._temp_descriptor.close()


class FanControl:
    def __init__(self, ip=None, port=None):
        if port and ip:
            self.pi = pigpio.pi(ip, port)
        else:
            self.pi = pigpio.pi()

        self.pi.set_mode(FAN_GPIO, pigpio.OUTPUT)
        self.pi.set_PWM_frequency(FAN_GPIO, PWM_FREQUENCY_HZ)
        self.pi.set_PWM_range(FAN_GPIO, 100)

        self._duty = 0

    @property
    def duty(self):
        return self._duty

    @duty.setter
    def duty(self, value):
        if value < 0:
            self._duty = 0
        elif value > 100:
            self._duty = 100
        else:
            self._duty = value
        self.pi.set_PWM_dutycycle(FAN_GPIO, self._duty)

    def __del__(self):
        self.pi.set_PWM_dutycycle(FAN_GPIO, 0)
        self.pi.set_mode(FAN_GPIO, pigpio.INPUT)
        self.pi.stop()


class PIDController:
    def __init__(self):
        self.pid = PID(-5, 0.01, 0.1, setpoint=TEMP_MAINTAIN)
        self.pid.output_limits = (DUTY_LOW_LIMIT, DUTY_HIGH_LIMIT)
        self.pid.sample_time = 2.5

    def pid_run(self, temp_sensor, fan_control):
        fan_control.duty = 0

        while True:
            temp = temp_sensor.temp

            if temp < TEMP_CUTOFF:
                fan_control.duty = 0

            if temp > TEMP_MAINTAIN:
                while temp > TEMP_CUTOFF:
                    duty = self.pid(temp)
                    fan_control.duty = duty
                    time.sleep(0.5)
                    temp = temp_sensor.temp

            time.sleep(10)


def main():
    temp_sensor = CPUTemperatureSensor()
    fan_control = FanControl()
    pid_control = PIDController()
    pid_control.pid_run(temp_sensor, fan_control)


if __name__ == "__main__":
    main()
