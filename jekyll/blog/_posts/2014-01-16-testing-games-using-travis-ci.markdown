---
layout: post
title:  Testing LÖVE Games Using Travis CI
date:   2014-01-16 08:00:00
author: Kyle Conroy
---

One of our main goals at StackMachine is to bring game development up to speed
with the rest of the software engineering industry. Best practices such as unit
testing, continuous integration, and continuous delivery have yet to make it
into the mainstream game development pipeline.

One of the easiest things you can do to improve your process is start testing
your LÖVE modules and games using Travis CI. Travis is a free continuous
integration service for open source projects. It's deeply integrated into
GitHub, making it easy to enable and use. Several popular projects, such as
[Journey to the Center of Hawkthorne][hawk] and [Glove][glove], use Travis to
power their tests.

## The Setup

Before you can begin, you'll need to login into Travis using your GitHub
account. From there, you'll be able to enable testing on specific repositories.

Travis knows how to run your tests by looking for a `.travis.yml` file in your
repository. Below is a sample configuration you can use for your LÖVE game. You
can also check out the [.travis.yml][gloveyml] for Glove.

{% highlight yaml %}
language: erlang
before_install:
  - "export DISPLAY=:99.0"
  - "sh -e /etc/init.d/xvfb start"
install:
  - mkdir -p $TRAVIS_BUILD_DIR/share/love/
env:
  matrix:
    - LOVE_VERSION=0.8.0
    - LOVE_VERSION=0.9.0
  global:
    - XDG_DATA_HOME="$TRAVIS_BUILD_DIR/share"
script: make test
{% endhighlight %}

A few notes about this configuration:

We set the language  to erlang because Travis has yet to officially support
Lua. We aren't installing Lua because the tests are run using LÖVE
itself.

On Linux, LÖVE uses `~/.local/share/love/` for storing game data. This folder
isn't writable in the Travis environment, so we need to set the `XDG_DATA_HOME`
environment variable to a writable path.

Lastly, we make sure to start a virtual display so that LÖVE can run without an
actual display attached to the session.

## Running Tests

Glove uses [lovetest][lovetest] to run its unit and functional tests. The
reason lovetest is used over more common test runners such as [lunit][lunit]
and [busted][busted] is that we want access to the `love` module from our
tests.

Below is a sample Makefile for running LÖVE in the Travis environment. It
supports both 0.8.0 and 0.9.0, as your game or module may use both.

{% highlight make %}
ifeq ($(LOVE_VERSION), 0.9.0)
  LOVE = /usr/bin/love9
else
  LOVE = /usr/bin/love8
endif

test: $(LOVE)
	$(LOVE) path/to/game --test

/usr/bin/love8:
	wget https://bitbucket.org/rude/love/downloads/love_0.8.0-0precise1_amd64.deb
	-sudo dpkg -i love_0.8.0-0precise1_amd64.deb
	sudo apt-get update -y
	sudo apt-get install -f -y
	sudo ln -s /usr/bin/love /usr/bin/love8

/usr/bin/love9:
	sudo add-apt-repository -y ppa:bartbes/love-stable
	sudo apt-get update -y
	sudo apt-get install -y love
	sudo ln -s /usr/bin/love /usr/bin/love9
{% endhighlight %}


This sample is a stripped-down version of [Glove's Makefile][makefile] for
Glove.

You'll need to change `path/to/game` to point to the directory that contains
your `main.lua`.


## Trouble Shooting

Running LÖVE in a headless environment can be tricky. During startup, you'll
see a list of scary errors such as these.

    shm_open() failed: Permission denied
    AL lib: pulseaudio.c:612: Context did not connect: Access denied
    ALSA lib confmisc.c:768:(parse_card) cannot find card '0'
    ALSA lib conf.c:4241:(_snd_config_evaluate) function snd_func_card_driver returned error:
    ALSA lib pcm.c:2217:(snd_pcm_open_noupdate) Unknown PCM default
    AL lib: alsa.c:512: Could not open playback device 'default':
    AL lib: oss.c:169: Could not open /dev/dsp: Permission denied

Don't worry about these errors. They stem from the lack of a valid audio
backend in the CI environment. They have no effect on your tests.

## Go Now and Test

With this setup you should be able to add continuous integration to your LÖVE
module or game in a matter of minutes. Having tests run on every commit make it
more likely you'll spot bugs earlier and ship fewer regressions.

[travis]: https://travis-ci.org/
[hawk]: https://github.com/hawkthorne/hawkthorne-journey
[glove]: https://github.com/stackmachine/glove
[gloveyml]: https://github.com/stackmachine/glove/blob/master/.travis.yml
[lovetest]: https://github.com/stackmachine/lovetest
[lunit]: http://www.mroth.net/lunit/
[busted]: http://olivinelabs.com/busted/
[makefile]: https://github.com/stackmachine/glove/blob/master/Makefile
