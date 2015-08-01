from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

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
            progress_bar=util.make_progress_bar(util.get_percent_elapsed_from_time_strings(position, duration)),
            volume=kwargs.get('volume') or self.volume,
        )

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
