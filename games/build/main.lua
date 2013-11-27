local reporter = require 'sparkle/reporter'
local logging = require 'sparkle/logging'
local tasks = require 'sparkle/tasks'

function love.errhand(msg)
  reporter.log(msg)
end

function love.releaseerrhand(msg)
  reporter.log(msg)
end

function love.load(arg)
  local logger = logging.new('foo')
  logger:info("Successly started")
  tasks.track('Foo Bar')
  local a = {}
  local b = a.b.c
end

function love.update(dt)
end

function love.draw(dt)
  love.graphics.print("KID PIX", 30, 30)
end
