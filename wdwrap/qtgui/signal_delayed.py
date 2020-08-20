#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
from typing import Optional

import PySide2
from PySide2.QtCore import Signal, Slot, QObject


_logger = None

def logger():
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger('sig delay')
    return _logger


class SignalDelayedPermanentTimer:
    """Qt Signals delayed and grouped

    Use instances of SignalDelayedPermanentTimer as "normal" instance variables (initialized in the `__init__`)
    Subsequent calls to `emit` before signal get fired, will be grouped, `*args` will be replaced
     by the last `emit`, while `**kwargs` will be *updated* by subsequent calls.
    """

    class _HasSignalAndTimer(QObject):
        signal = Signal(object)

        def __init__(self, timer_handler):
            super().__init__()
            self.timer_handler = timer_handler

        def timerEvent(self, event: PySide2.QtCore.QTimerEvent):
            super().timerEvent(event)
            self.timer_handler(event)

    def __init__(self, name: Optional[str] = None, ping: int = 200, enable: bool = True) -> None:
        super().__init__()
        self.scheduled = False
        self.ping = ping
        if name is None:
            name = str(id(self))
        self.name = name
        self.arg = None
        self._timerts_ids = []
        self.signal = self._HasSignalAndTimer(timer_handler=lambda event: self._emit_scheduled())
        if enable:
            self.enable()

    def enable(self, enable: bool = True):
        for tid in self._timerts_ids:
            self.signal.killTimer(tid)  # idle timer
        self._timerts_ids = []
        if enable:
            # self._timerts_ids.append(self.signal.startTimer(0))  # idle timer
            # if self.ping != 0:
            self._timerts_ids.append(self.signal.startTimer(self.ping))  # recurring timer

    def connect(self, *args, **kwargs):
        logger().info(f'Signal {self.name} connecting')
        self.signal.signal.connect(*args, **kwargs)

    def disconnect(self, *args, **kwargs):
        logger().info(f'Signal {self.name} disconnecting')
        try:
            self.signal.signal.disconnect(*args, **kwargs)
        except RuntimeError:
            pass

    def __call__(self, arg):
        logger().info(f'Signal {self.name} called')
        self.signal.signal(arg)

    def emit(self, arg):
        """emit on idle"""
        if self.scheduled:
            logger().info(f'Signal {self.name} rescheduling')
        else:
            logger().info(f'Signal {self.name} scheduling')
        self.scheduled = False
        self.arg = arg
        # TODO: try/except on-shot-timer to reduce waiting time, if fails (not qt thread) ping timer do the job
        self.scheduled = True

    @Slot()
    def _emit_scheduled(self):
        if self.scheduled:
            # TODO: use lock (QLock?)
            arg = self.arg
            self.arg = None
            self.scheduled = False
            logger().info(f'Signal {self.name} emitting')
            self.signal.signal.emit(arg)


# class SignalDelayedSingleShotTimer(Generic[T]):
#     """Qt Signals delayed and grouped
#
#     Use instances of SignalDelayed as "normal" instance variables (initialized in the `__init__`)
#     Signal will be passed to connected objects on idle, optionally with delay.
#     Subsequent calls to `emit` before signal get fired, will be grouped, `*args` will be replaced
#      by the last `emit`, while `**kwargs` will be *updated* by subsequent calls.
#     """
#
#     class _HasSignal(QObject):
#         signal = Signal(T)
#
#     def __init__(self, name: Optional[str] = None) -> None:
#         super().__init__()
#         self.signal = self._HasSignal()
#         if name is None:
#             name = str(id(self))
#         self.name = name
#         self.args = []
#         self.kwargs = {}
#         self.timer = None
#
#     def connect(self, *args, **kwargs):
#         logger().info(f'Signal {self.name} connecting')
#         self.signal.signal.connect(*args, **kwargs)
#
#     def disconnect(self, *args, **kwargs):
#         logger().info(f'Signal {self.name} disconnecting')
#         self.signal.signal.disconnect(*args, **kwargs)
#
#     def __call__(self, *args, **kwargs):
#         logger().info(f'Signal {self.name} called')
#         self.signal.signal(*args, **kwargs)
#
#     def emit(self, *args, **kwargs):
#         """emit on idle"""
#         self.emit_delayed(*args, delay_msec=0, **kwargs)
#
#     def emit_delayed(self, *args, delay_msec: int, **kwargs):
#         """emit on idle with delay"""
#         if self.timer and self.timer.isActive():
#             logger().info(f'Signal {self.name} rescheduling, delay {delay_msec} msec')
#         else:
#             logger().info(f'Signal {self.name} scheduling, delay {delay_msec} msec')
#         self.args = args
#         self.kwargs.update(kwargs)
#
#         self.stop_timer()
#         self.timer = QTimer()
#         self.timer.setSingleShot(True)
#         self.timer.timeout.connect(self._emit_scheduled)
#
#         self.timer.start(int(delay_msec))
#
#     def stop_timer(self):
#         if self.timer is not None:
#             self.timer.timeout.disconnect()
#             self.timer.stop()
#             self.timer = None
#
#     @Slot()
#     def _emit_scheduled(self):
#         logger().info(f'Signal {self.name} emitting')
#         args = self.args
#         kwargs = self.kwargs
#         self.stop_timer()
#         self.args = []
#         self.kwargs = {}
#         self.signal.signal.emit(*args, **kwargs)
#
