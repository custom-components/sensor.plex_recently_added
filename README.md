# plex_recently_added

## Super early version for testing

This is a component to feed the associated Lovelace card: [Upcoming_Media_Card](https://github.com/custom-cards/upcoming-media-card)

**Component:**

    - platform: plex_recently_added
      token: { your plex token || required}
      ssl: {true or false || optional, default 'false'}
      host: { IP address || optional, default 'localhost' }
      port: { port || optional, default '32400'}
      item_count: { Number of recent downloads to show || optional, default '5'}


**Lovelace:**

    - type: custom:upcoming-media-card
      entity: sensor.plex_recently_added
