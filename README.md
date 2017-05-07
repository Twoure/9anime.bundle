9anime
===========

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/87e4130322374e9e900fcc763a27eb4e)](https://www.codacy.com/app/twoure/9anime-bundle?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Twoure/9anime.bundle&amp;utm_campaign=Badge_Grade) [![GitHub issues](https://img.shields.io/github/issues/Twoure/9anime.bundle.svg?style=flat)](https://github.com/Twoure/9anime.bundle/issues) [![](https://img.shields.io/github/release/Twoure/9anime.bundle.svg?style=flat)](https://github.com/Twoure/9anime.bundle/releases)

This plugin creates a new Video Channel within [Plex Media Server](https://plex.tv/) (PMS) to view [Anime](https://en.wikipedia.org/wiki/Anime) from [9anime.to](https://9anime.to/).  It is currently under development and as such, should be considered alpha software and potentially unstable.

> **Note:** the author of this plugin has no affiliation with [9anime.to](https://9anime.to/) nor the owners of the content that they host.

## Features

- Watch Anime TV & Movies (quality ranges from 360p to 1080p)
- Search Anime
- Update from within the Channel

## [Changelog](Changelog.md#changelog)

## Channel Support

##### Plex Media Server:
- Tested Working:
  - Ubuntu 14.04 LTS: PMS version 1.6.1

##### Plex Clients:
- Tested Working:
  - Android (7.1.2) (Plex Client App, v5.8.0.475)
  - Plex Web (3.5.0)
  - Chromecast

## Install

- This channel can be installed via [WebTools.bundle](https://github.com/dagalufh/WebTools.bundle) or manually follow the directions below.
- Download the latest [![](https://img.shields.io/github/release/Twoure/9anime.bundle.svg?style=flat)](https://github.com/Twoure/9anime.bundle/releases) and install **9anime** by following the Plex [instructions](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-) or the instructions below.
  - Unzip and rename the folder to **9anime.bundle**
  - Copy **9anime.bundle** into the PMS [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory
  - Unix based platforms need to `chown plex:plex -R 9anime.bundle` after moving it into the [Plug-ins](https://support.plex.tv/hc/en-us/articles/201106098-How-do-I-find-the-Plug-Ins-folder-) directory _(`user:group` may differ by platform)_
  - **Restart PMS**

## To Do

- Switch to `TVShow` and `Season` objects
- Add bookmark support

## Support

- [Plex Forums Thread](https://forums.plex.tv/discussion/251439)
- [GitHub Issues](https://github.com/Twoure/9anime.bundle/issues)
