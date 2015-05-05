import threading
import time







class RegulatorParameters:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		
		
		self.__absolute_angle_period = None
		self.__right_absolute_angle  = None
		self.__left_absolute_angle   = None
		
		
		
	def copy(self):
		regulator_parameters = RegulatorParameters()
		
		regulator_parameters.__absolute_angle_period = \
			self.__absolute_angle_period
			
		regulator_parameters.__right_absolute_angle = \
			self.__right_absolute_angle
			
		regulator_parameters.__left_absolute_angle = \
			self.__left_absolute_angle
			
		return regulator_parameters
		
		
		
	@property
	def is_correct(self):
		is_correct = True
		
		is_correct &= self.__absolute_angle_period is not None
		is_correct &= self.__right_absolute_angle is not None
		is_correct &= self.__left_absolute_angle is not None
		
		return is_correct
		
		
		
		
		
	@property
	def absolute_angle_period(self):
		return self.__absolute_angle_period
		
		
		
	@absolute_angle_period.setter
	def absolute_angle_period(self, period):
		if period <= 0.0:
			# Период должен быть положительным числом
			raise Exception() #!!!!! Создавать хорошие исключения
			
		self.__absolute_angle_period = period
		
		
		
	@property
	def right_absolute_angle(self):
		return self.__right_absolute_angle
		
		
		
	@right_absolute_angle.setter
	def right_absolute_angle(self, absolute_angle):
		self.__right_absolute_angle = absolute_angle
		
		
		
	@property
	def left_absolute_angle(self):
		return self.__left_absolute_angle
		
		
		
	@left_absolute_angle.setter
	def left_absolute_angle(self, absolute_angle):
		self.__left_absolute_angle = absolute_angle
		
		
		
		
		
		
		
NONE_STATE  = 0
RIGHT_STATE = 2 ** 0
LEFT_STATE  = 2 ** 1
BOTH_STATE  = RIGHT_STATE | LEFT_STATE







class Regulator:
	__states = {
		NONE_STATE,
		RIGHT_STATE,
		LEFT_STATE,
		BOTH_STATE,
	}
	
	
	
	
	
	def __init__(self, machine, parameters, *args, **kwargs):
		if not parameters.is_correct:
			# Заданы не все параметры
			raise Exception() #!!!!! Создавать хорошие исключения
			
			
		super().__init__(*args, **kwargs)
		
		
		self._lock_object = threading.RLock()
		
		self.__machine    = machine
		self.__parameters = parameters.copy()
		
		self.__state_time_mark = time.time()
		self.__state           = NONE_STATE
		
		
		
	def _lock(method):
		def result_method(self, *args, **kwargs):
			with self._lock_object:
				return method(self, *args, **kwargs)
				
		return result_method
		
		
		
		
		
	@property
	def machine(self):
		return self.__machine
		
		
		
	@property
	def parameters(self):
		return self.__parameters.copy()
		
		
		
		
		
	@_lock
	def set_state(self, state):
		if state not in Regulator.__states:
			# Передано некорректное состояние
			raise Exception() #!!!!! Создавать хорошие исключения
			
		if self.__state != state:
			self.__state           = state
			self.__state_time_mark = time.time()
			
			
			
	@_lock
	def control(self, write_message):
		def set_steering_angle(absolute_angle):
			max_state_time = self.__parameters.absolute_angle_period
			
			state_time = time.time() - self.__state_time_mark
			state_time = min(state_time, max_state_time)
			angle      = absolute_angle * (state_time / max_state_time) ** 0.5
			
			self.__machine.set_steering_angle(angle)
			write_message(angle)
			
			
		if self.__state == RIGHT_STATE:
			set_steering_angle(self.__parameters.right_absolute_angle)
			
		elif self.__state == LEFT_STATE:
			set_steering_angle(self.__parameters.left_absolute_angle)
			