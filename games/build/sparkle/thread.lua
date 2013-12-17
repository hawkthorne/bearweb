require "love.filesystem"
require "love.event"

local glove = require("sparkle/glove")
local sparkle = require("sparkle")

local thread = glove.thread.getThread()

local version = thread:demand('version')
local url = thread:demand('url')

local function statusCallback(finished, status, percent)
  thread:set('finished', finished)
  thread:set('message', status)
  thread:set('percent', percent)
end

sparkle.update(version, url, statusCallback)

