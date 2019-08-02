# Plex Recently Added Component

Home Assistant component to feed [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card) with
Plex's recently added media.</br>
This component does not require, nor conflict with, the default Plex components.</br></br>
<link href="https://fonts.googleapis.com/css?family=Lato&subset=latin,latin-ext" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/FgwNR2l"><img src="https://www.buymeacoffee.com/assets/img/BMC-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:5px">If you feel I deserve it, you can buy me a coffee</span></a></br>
</br>

### If you're having issues, check out the [troubleshooting guide](https://github.com/custom-cards/upcoming-media-card/blob/master/troubleshooting.md) before posting an issue or asking for help on the forums.

## Installation:
1. Install this component by copying [these files](https://github.com/custom-components/sensor.plex_recently_added/tree/master/custom_components/plex_recently_added) to `custom_components/plex_recently_added/`.
2. Install the card: [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card)
3. Add the code to your `configuration.yaml` using the config options below.
4. Add the code for the card to your `ui-lovelace.yaml`. 
5. **You will need to restart after installation for the component to start working.**

### Options

| key | default | required | description
| --- | --- | --- | ---
| name | Plex_Recently_Added | no | Name of the sensor. Useful to make multiple sensors with different libraries.
| token | | yes | Your Plex token [(Find your Plex token)](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
| host | localhost | yes | The host Plex is running on.
| port | 32400 | yes | The port Plex is running on.
| ssl | false | no | Set to true if you use SSL to access Plex.
| max | 5 | no | Max number of items to show in sensor.
| download_images | true | no | Setting this to false will turn off downloading of images, but will require certain Plex settings to work. See below.
| img_dir | '/custom-lovelace/upcoming-media-card/images/plex/' | no | This option allows you to choose a custom directory to store images in if you enable download_images.
| ssl_cert | false | no | If you provide your own SSL certificate in Plex's network settings set this to true.
| section_types | movie, show | no | Allows you to specify which section types to consider [movie, show].

#### By default this addon automatically downloads images from Plex to your /www/custom-lovelace/upcoming-media-card/ directory. The directory is automatically created & only images reported in the upcoming list are downloaded. Images are small in size and are removed automatically when no longer needed. Currently & unfortunately, this may not work on all systems.

#### If you prefer to not download the images you may set download_images to false, but you either have to set "Secure connections" to "preferred" or "disabled" (no SSL) or have a custom certificate set (these options are found in your Plex server's network settings). This is needed because the default SSL certificate supplied by Plex is for their own domain and not for your Plex server. Your server also needs to be "fully accessible outside your network" if you wish to be able to see images remotely. If your Plex server provides it's own certificate you only need to set ssl_cert to true and download_images to false. 

</br></br>
**Do not just copy examples, please use config options above to build your own!**
### Sample for configuration.yaml:
```yaml
    sensor:
    - platform: plex_recently_added
      token: YOUR_PLEX_TOKEN
      host: 192.168.1.42
      port: 32400
      ssl: true
      ssl_cert: false
      download_images: false
      max: 5
      section_types:
      - movie
      - show
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
```

## \*Currently genres, rating, and studio only work for Movies
### Card Content Defaults

| key | default | example |
| --- | --- | --- |
| title | $title | "The Walking Dead" |
| line1 | $episode | "What Comes After" |
| line2 | $day, $date $time | "Monday, 10/31 10:00 PM" Displays time of download.|
| line3 | $number - $rating - $runtime | "S01E12 - ★ 9.8 - 01:30"
| line4 | $genres | "Action, Adventure, Comedy" |
| icon | mdi:eye-off | https://materialdesignicons.com/icon/eye-off

