import os
import logging


class SingleInstanceMetaClass(type):
    def __init__(self, name, bases, dic):
        self.__single_instance = None
        super().__init__(name, bases, dic)

    def __call__(cls, *args, **kwargs):
        if cls.__single_instance:
            return cls.__single_instance
        single_obj = cls.__new__(cls)
        single_obj.__init__(*args, **kwargs)
        cls.__single_instance = single_obj
        return single_obj


class Logger(metaclass=SingleInstanceMetaClass):
    def __init__(self, name, file=True, format_str="%(asctime)s [%(pathname)s:%(lineno)s - %(levelname)s ] %(message)s",
               date_format='%Y-%m-%d %H:%M:%S'):
        self.name = name
        self.file = file
        self.format_str = format_str
        self.date_format = date_format
        self.handler = logging.FileHandler(self.name) if self.file else logging.StreamHandler()

    def setup(self):
        logger = logging.getLogger(self.name)
        self.handler.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt=self.format_str, datefmt=self.date_format)
        self.handler.setFormatter(formatter)
        logger.addHandler(self.handler)
        return logger


