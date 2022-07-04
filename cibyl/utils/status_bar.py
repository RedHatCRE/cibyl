"""
#    Copyright 2022 Red Hat
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
"""

import itertools
import threading
import time

from cibyl.utils.colors import Colors


class StatusBar(threading.Thread):
    """A class representation of a status bar. The status bar displays
    an animation to the user to let them know the program is working in the
    background.

    The status bar is implemented as a context manager that starts a thread
    that displays the animation when the code execution reaches a given code
    section and destroys the thread when the execution leaves the section.

    :param status_text: Text that is displayed to the user
    :type status_text: str
    :param update_frequency: How often should the status bar be updated
    :type update_frequency: float
    """

    def __init__(self, status_text: str, update_frequency: float = 0.5):
        """Creates an instance of the StatusBar class"""
        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        self.status_text = status_text
        self.update_frequency = update_frequency

    def run(self) -> None:
        """Prints the animation to stdout"""
        characters = ['.   ', ' .  ', '  . ', '   .']
        for character in itertools.cycle(characters):
            animation_text = Colors.green(f'{self.status_text} {character}')
            print(animation_text, end='\r', flush=True)
            time.sleep(self.update_frequency)

            if self.stopEvent.isSet():
                eraser = ' ' * len(animation_text)
                print(eraser, end='\r', flush=True)
                return

    def stop(self):
        """Stops the animation"""
        self.stopEvent.set()
        self.join()

    def __enter__(self):
        """Starts the animation when entering a given code section"""
        self.start()
        return self

    def __exit__(self, *args, **kwargs):
        """Stops the animation when leaving a given code section"""
        self.stop()
