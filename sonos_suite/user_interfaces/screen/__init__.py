from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import npyscreen
import soco.config


class DeviceBoundSlider(npyscreen.Slider):
    def __init__(self, *args, **kwargs):
        self.device = kwargs.pop('device')
        super(DeviceBoundSlider, self).__init__(*args, **kwargs)


class SliderTime(DeviceBoundSlider):
    def translate_value(self):
        now_playing = self.device.get_current_track_info()
        return '{position} / {duration}'.format(position=now_playing['position'], duration=now_playing['duration'])


class TitleSliderTime(npyscreen.TitleSlider):
    _entry_type = SliderTime


class SliderVolume(DeviceBoundSlider):
    def when_value_edited(self):
        self.device.volume = int(self.value)


class TitleSliderVolume(npyscreen.TitleSlider):
    _entry_type = SliderVolume


class SonosController(npyscreen.Form):
    def __init__(self, device, *args, **kwargs):
        assert isinstance(device, soco.config.SOCO_CLASS)
        self.device = device

        super(SonosController, self).__init__(*args, **kwargs)

    def create(self):
        now_playing = self.device.get_current_track_info()

        self.player_name = self.add(
            npyscreen.TitleFixedText,
            name='Selected Player',
            value=self.device.player_name,
            editable=False
        )
        self.player_name = self.add(
            npyscreen.TitleFixedText,
            name='Selected Group',
            value=self.device.group.label,
            editable=False
        )

        self.artist = self.add(npyscreen.TitleFixedText,  name='Artist', value=now_playing['artist'], editable=False)
        self.album = self.add(npyscreen.TitleFixedText, name='Album', value=now_playing['album'], editable=False)
        self.title = self.add(npyscreen.TitleFixedText, name='Title', value=now_playing['title'], editable=False)

        self.player_status = self.add(
            npyscreen.TitleFixedText,
            name='Status',
            value=self.device.get_current_transport_info().get('current_transport_state', 'UNKNOWN'),
            editable=False
        )
        self.position = self.add(
            TitleSliderTime,
            name='Position',
            label=True,
            value=self.device._get_percent_elapsed_from_time_strings(now_playing['position'], now_playing['duration']),
            editable=False,
            device=self.device,
        )
        self.volume = self.add(
            TitleSliderVolume,
            name='Volume',
            label=True,
            value=int(self.device.volume),
            device=self.device
        )

    def afterEditing(self):
        self.parentApp.setNextForm(None)


class MainApplication(npyscreen.NPSAppManaged):
    def __init__(self, device, *args, **kwargs):
        self.device = device
        super(MainApplication, self).__init__(*args, **kwargs)

    def onStart(self):
        controller = self.addForm('MAIN', SonosController, name='Sonos App Form', device=self.device)


if __name__ == '__main__':
    app = MainApplication().run()
