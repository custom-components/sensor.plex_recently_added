# Plex Recently Added Component

Home Assistant component to feed [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card) with
Plex's recently added media.</br>
This component does not require, nor conflict with, the default Plex components.</br></br>

### **New Features! ⭐**
 - Added support for Plex 'deep_links' in sensor attributes (Direct URLs to each TV Episode & Movie on Plex Web).
 - Added support for 'season_num' & 'episode_num' in sensor attributes for TV Episodes.

### Issues
Read through these two resources before posting issues to GitHub or the forums.
 - [upcoming-media-card troubleshooting guide](https://github.com/custom-cards/upcoming-media-card/blob/master/troubleshooting.md)
 - [@thomasloven's lovelace guide](https://github.com/thomasloven/hass-config/wiki/Lovelace-Plugins).

## Installation:
1. Install this component by copying [these files](https://github.com/custom-components/sensor.plex_recently_added/tree/master/custom_components/plex_recently_added) to `custom_components/plex_recently_added/`.
2. Install the card: [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card)
3. Add the code for the card to your `ui-lovelace.yaml`.
4. **You will need to restart after installation for the component to start working.**

### Adding device
To add the **Plex Recently added** integration to your Home Assistant, use this My button:

<a href="https://my.home-assistant.io/redirect/config_flow_start?domain=plex_recently_added" class="my badge" target="_blank"><img src="https://my.home-assistant.io/badges/config_flow_start.svg"></a>

<details><summary style="list-style: none"><h3><b style="cursor: pointer">Manual configuration steps</b></h3></summary>

If the above My button doesn’t work, you can also perform the following steps manually:

- Browse to your Home Assistant instance.

- Go to [Settings > Devices & Services](https://my.home-assistant.io/redirect/integrations/).

- In the bottom right corner, select the [Add Integration button].(https://my.home-assistant.io/redirect/config_flow_start?domain=plex_recently_added)

- From the list, select **Plex Recently added**.

- Follow the instructions on screen to complete the setup.
</details>

The number of items in the sensor, library types, libraries in general, excluded words, and show "on deck" options can be changed later.

**Do not just copy examples, please use config options above to build your own!**

## FAQ:
### When I tried it said *"User already configured"*
This is because the integration uses the Plex token as a part of its *unique_id*, so it does not collide with other instances of the same integration.

### I want to change the config of the integration, how do I do it?
This is very simple, when you go to the *'Settings/Devices & services/Plex Recently Added'* you will see your instance of the Plex Recently Added integration and on the right side you will see **Configure** button, when you press it you can change all necessary config you might need to change and click submit, the instance then should restart and show new values basen on your new settings.
</br><small>(If you want to change Plex address, token or sensors prefix name you will need to readd the integration with your new parameters)</small>

### The number of items in the sensor is not the amount I set it to be
The sensor you most likely mean is the merged sensor which shows all the data (also sorted) that are in the other sensors, meaning if you've set your man number if values to 7 and you've got 3 section types (movie, show, artist) the total number of items in the merged sensor will be 21 (7 *<small>(for max)</small>* * 3 *<small>(for section types)</small>*)

### My sensor is not showing any values, but there are no errors
This may be caused by incorrectly set *Libraries to consider*, you can change them in [Config](#i-want-to-change-the-config-of-the-integration-how-do-i-do-it), where if you've configured your Plex token and address right will now show all libraries in the dropdown selection.

### Card Content Defaults

| key   | default                      | example                                             |
| ----- | ---------------------------- | --------------------------------------------------- |
| title | $title                       | "The Walking Dead"                                  |
| line1 | $episode                     | "What Comes After"                                  |
| line2 | $day, $date $time            | "Monday, 10/31 10:00 PM" Displays time of download. |
| line3 | $number - $rating - $runtime | "S01E12 - ★ 9.8 - 01:30"                            |
| line4 | $genres                      | "Action, Adventure, Comedy"                         |
| icon  | mdi:eye-off                  | https://materialdesignicons.com/icon/eye-off        |
