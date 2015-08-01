from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import logging

from soco.core import SoCo


class SonosDevice(SoCo):
    def sleep_timer(self, duration_in_minutes=None):
        if duration_in_minutes is not None:
            duration_in_minutes = int(duration_in_minutes)
            hour = str(duration_in_minutes // 60)
            minutes = str(duration_in_minutes % 60)
            formatted_duration = '{}:{}:00'.format(hour.zfill(2), minutes.zfill(2))
            self.group.coordinator.avTransport.ConfigureSleepTimer([
                ('InstanceID', 0),
                ('NewSleepTimerDuration', formatted_duration)
            ])

        status = self.group.coordinator.avTransport.GetRemainingSleepTimerDuration([
            ('InstanceID', 0)
        ])
        return '{} remaining'.format(status.get('RemainingSleepTimerDuration') or '00:00:00')

    def current(self):
        if self.is_coordinator is False:
            logging.warning('Selected device is not its own group coordinator!')
        return self._make_current_display()

    def build_current_display(self, **kwargs):
        return self._make_current_display(**kwargs)

    def _make_current_display(self, **kwargs):
        info = self.get_current_track_info()
        template = """
        Artist:     {artist}
        Album:      {album}
        Title:      {title}
        {radio_data}

        Status:     {player_status}
        Position:   {current_position} / {total_duration}
                    {progress_bar}
        Volume:     {volume}
        """
        radio_template = 'Radio Show: {radio_show}'

        position = kwargs.get('current_position') or info['position']
        duration = kwargs.get('total_duration') or info['duration']

        return template.format(
            artist=kwargs.get('artist') or info['artist'],
            album=kwargs.get('album') or info['album'],
            title=kwargs.get('title') or info['title'],
            player_status=kwargs.get('player_status') or self.get_current_transport_info().get(
                'current_transport_state',
                'UNKNOWN'
            ),
            radio_data=radio_template.format(radio_show=kwargs['radio_show']) if kwargs.get('radio_show') else '',
            current_position=position,
            total_duration=duration,
            progress_bar=self._make_progress_bar(self._get_percent_elapsed_from_time_strings(position, duration)),
            volume=kwargs.get('volume') or self.volume,
        )

    @property
    def progress(self):
        info = self.get_current_track_info()
        position = info['position']
        duration = info['duration']
        return self._make_progress_bar(self._get_percent_elapsed_from_time_strings(position, duration))

    @staticmethod
    def _make_progress_bar(percent, width=48, fill_char='=', padding_char='-'):
        template = '[{fill}{padding}]'
        if percent != 0:
            fill_width = int(width * percent) or 1
        else:
            fill_width = 0
        padding_width = width - fill_width
        try:
            assert fill_width + padding_width == width
        except AssertionError:
            print(fill_width, '+', padding_width, '==', fill_width + padding_width, '!=', width)
        return template.format(
            fill=fill_char * fill_width,
            padding=padding_char * padding_width
        )

    @staticmethod
    def _get_percent_elapsed_from_time_strings(position_string, duration_string):
        if not position_string:
            position_string = '00:00:00'

        if not duration_string:
            duration_string = '00:00:00'

        position_time = datetime.datetime.strptime(position_string, '%H:%M:%S').time()
        duration_time = datetime.datetime.strptime(duration_string, '%H:%M:%S').time()

        time_to_seconds = lambda t: (3600 * t.hour) + (60 * t.minute) + (1 * t.second)
        position_seconds = time_to_seconds(position_time)
        duration_seconds = time_to_seconds(duration_time)

        try:
            return position_seconds / duration_seconds
        except ZeroDivisionError:
            return 1

    @property
    def available_command_names(self):
        return [command_name for command_name in dir(self) if command_name[0] != '_']

    @property
    def select(self):
        return True

    def help(self, command_name=None):
        """Lists all available commands, or, if a specific command is given, displays documentation for that command
        """
        if command_name is None:
            output = 'Available Commands:\n'
            for available_command in self.available_command_names:
                output += '\t{}\n'.format(available_command)
        else:
            # output = 'Showing help for command "{}":\n'.format(command_name)
            output = ''
            try:
                command_attribute = getattr(SonosDevice, command_name)
            except AttributeError:
                command_attribute = getattr(self, command_name)
            available_doc = getattr(command_attribute, '__doc__', '(No Documentation)')
            output += '\n{}\n'.format(available_doc)
        return output
