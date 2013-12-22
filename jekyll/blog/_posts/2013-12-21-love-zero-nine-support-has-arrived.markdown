---
layout: post
title:  Announcing Support for LÖVE 0.9.0
date:   2013-12-22 00:00:00
author: Kyle Conroy
foo: bar
categories: features
---

![Baby Inspector](/static/img/baby.jpg)

Version 0.9.0 (codename Baby Inspector) was released last week after a year in
development. It's a huge milestone for the engine and we're happy to have been
a part of the release. StackMachine powers [Nightly LÖVE][nightly], [the
Jenkins infrastructure][jenkins] behind nightly builds of LÖVE game engine.
Users have been testing out 0.9.0 for months before the official release,
finding bugs and providing valuable feedback.

Today StackMachine launches full support for 0.9.0. To enable 0.9.0 for your
game, just make sure to include the following in your `conf.lua`:

    function love.conf(t)
      t.version = "0.9.0"
    end

If you're unfamiliar with `conf.lua`, read the [Config Files][config] over on
the LÖVE wiki. To maintain backwards compatibility, games without 0.9.0
declared in `conf.lua` will continue to use version 0.8.0 of the engine.

We've got more exciting features planned over the next few weeks, so
[subscribe][rssfeed] and stay tuned.

[nightly]: http://love2d.org/builds
[jenkins]: http://ci.projecthawkthorne.com
[config]: http://www.love2d.org/wiki/Config_Files
[rssfeed]: http://localhost:8000/blog/feed.xml
