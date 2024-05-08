This component feeds [Upcoming Media Card](./146783593) with Plex's recently added media.

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
