local sparkle = require 'sparkle'
local reporter = require 'sparkle/reporter'
local tasks = require 'sparkle/tasks'
local config = require 'sparkle/config'

function love.errhand(msg)
  reporter.log(msg)
end

function love.releaseerrhand(msg)
  reporter.log(msg)
end

local cmdargs = {}
local updater = nil
local logo = nil
local message = ""
local time = 0
local updaterok = false
local progress = -1
local loaded = false

local function reset()
  require "oldmain"

  love.load(cmdargs)

  updater = nil
  logo = nil
  love.graphics.setColor(255, 255, 255, 255)
end

function love.load(arg)
  if loaded then
    return
  end

  tasks.track('opens')

  cmdargs = arg
  message = ""
  time = 0
  progress = 0
  logo = love.graphics.newImage('sparkle/splash.png')

  updater = sparkle.newUpdater(config.version, config.links.updates)
  updater:start()
  loaded = true
end

function love.update(dt)
  time = time + dt

  if updater and not updater:done() then
    local msg, percent, ok = updater:progress()

    updaterok = ok

    if msg ~= "" then
      message = msg
      progress = (percent or 1) % 100
    end

    return
  end

  if time < 2.5 then
    return
  end

  reset()
end

function love.draw()
  love.graphics.setColor(255, 255, 255, math.min(255, time * 100))

  local width = love.graphics.getWidth()
  local height = love.graphics.getHeight()

  if logo then
    love.graphics.draw(logo, width / 2 - logo:getWidth() / 2,
                       height / 2 - logo:getHeight() / 2)
  end

  if progress >= 0 then
    love.graphics.setColor(255, 255, 255)

    if updaterok then
      love.graphics.rectangle("line", 40, height - 75, width - 80, 10)
      love.graphics.rectangle("fill", 40, height - 75,  (width - 80) * progress / 100, 10)
    end

    love.graphics.printf(message, 40, height - 55, width - 80, 'center')
  end
end
