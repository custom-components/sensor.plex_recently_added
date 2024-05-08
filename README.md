# Plex Recently Added Component

Home Assistant component to feed [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card) with
Plex's recently added media.</br>
This component does not require, nor conflict with, the default Plex components.</br></br>

### **New Features! ⭐**
* Added support for Plex 'deep_links' in sensor attributes (Direct URLs to each TV Episode & Movie on Plex Web).
* Added support for 'season_num' & 'episode_num' in sensor attributes for TV Episodes.
<br>
<br>
### Issues
Read through these two resources before posting issues to GitHub or the forums.
* [troubleshooting guide](https://github.com/custom-cards/upcoming-media-card/blob/master/troubleshooting.md)
* [@thomasloven's lovelace guide](https://github.com/thomasloven/hass-config/wiki/Lovelace-Plugins).

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

- In the bottom right corner, select the [Add Integration button.](https://my.home-assistant.io/redirect/config_flow_start?domain=plex_recently_added)

- From the list, select **Plex Recently added**.

- Follow the instructions on screen to complete the setup.
</details>

The number of items in sensor, library types, libraries in general, excluded words and show "on deck" options can be changed later.

**Do not just copy examples, please use config options above to build your own!**
### Sample for minimal config needed in configuration.yaml:
```yaml
    sensor:
    - platform: plex_recently_added
      token: YOUR_PLEX_TOKEN
      host: 192.168.1.42
      port: 32400
```
### Sample for ui-lovelace.yaml:
```yaml
    - type: custom:upcoming-media-card
      entity: sensor.plex_recently_added
      title: Recently Downloaded
```
### Multiple sensor sample for configuration.yaml:
```yaml
  - platform: plex_recently_added
    name: Recently Added Movies # will create sensor.recently_added_movies
    token: !secret token
    host: !secret host
    port: 32400
    section_types:
      - movie

  - platform: plex_recently_added
    name: Recently Added TV  # will create sensor.recently_added_tv
    token: !secret token
    host: !secret host
    port: 32400
    section_types:
      - show
    exclude_keywords:
      - Walking dead
      - kardashians
```

## \*Currently genres, rating, and studio only work for Movies
### Card Content Defaults

| key   | default                      | example                                             |
| ----- | ---------------------------- | --------------------------------------------------- |
| title | $title                       | "The Walking Dead"                                  |
| line1 | $episode                     | "What Comes After"                                  |
| line2 | $day, $date $time            | "Monday, 10/31 10:00 PM" Displays time of download. |
| line3 | $number - $rating - $runtime | "S01E12 - ★ 9.8 - 01:30"                            |
| line4 | $genres                      | "Action, Adventure, Comedy"                         |
| icon  | mdi:eye-off                  | https://materialdesignicons.com/icon/eye-off        |
