---
layout: post
title:  Introducing Glove, the LÖVE Compatibility Library
date:   2014-01-15 00:00:00
author: Kyle Conroy
categories: features
---

With the recent release of LÖVE 0.9, there are now two popular versions of the
framework. While many games will be migrating to 0.9, many will choose to stay
with 0.8 for the foreseeable future. These two versions cause an issue for
developers looking to create libraries for LÖVE, as they need to support both
versions of the framework.

Inspired by [six][six], a compatibility library for Python 2 and 3, we're happy
to introduce [Glove][glove], a compatibility library for LÖVE 0.8 and 0.9.
Glove is a single Lua file, so it's easy to integrate. Once you've download the
file, migrating involves only a few changes. Let's look at code that only works
on 0.8

    function love.load()
      love.filesystem.mkdir('saves')
    end

[love.filesystem.mkdir][mkdir] was renamed in LÖVE 0.9 and will no longer work.
With Glove, you can easily make this code work across versions.

    local glove = require 'glove'
    
    function love.load()
      glove.filesystem.mkdir('saves')
    end

This code will now work across both versions of the LÖVE framework.

The StackMachine SDK for LÖVE is powered using Glove and we can't wait for the
library to grow. You can see a list of all the supported methods in the
[documentation][wiki] and contribute to the [code on GitHub][glove].

[six]: http://pythonhosted.org/six
[mkdir]: http://love2d.org/wiki/love.filesystem.mkdir
[wiki]: https://github.com/stackmachine/glove/wiki/Supported-Methods-and-Modules
[glove]: https://github.com/stackmachine/glove
