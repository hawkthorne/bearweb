local stackmachine = require 'stackmachine'
local reporter = require 'stackmachine/reporter'
local tasks = require 'stackmachine/tasks'
local logging = require 'stackmachine/logging'
local config = require 'stackmachine/config'
local utils = require 'stackmachine/utils'

function love.errhand(msg)
  reporter.log(msg)
end

function love.releaseerrhand(msg)
  reporter.log(msg)
end

local cmdargs = {}
local updater = nil
local downloading = false
local logo = nil
local message = ""
local time = 0
local updaterok = false
local progress = -1
local loaded = false
local logger = logging.new('foo')

local function reset()
  require "oldmain"

  love.load(cmdargs)

  updater = nil
  logo = nil
end

function love.load(arg)
  if loaded then return end

  local identity = ""

  if love.filesystem.getIdentity then
    identity = love.filesystem.getIdentity()
  end
    
  if config.identity and (identity == "" or identity == nil) then
    love.filesystem.setIdentity(config.identity)
  end

  tasks.track('opens')

  cmdargs = arg
  message = ""
  time = 0
  progress = 0

  updater = stackmachine.newUpdater(arg, config.version, config.links.updates)
  updater:start()
  loaded = true
end

function love.update(dt)
  time = time + dt

  if updater and not updater:done() then
    local msg, percent, ok = updater:progress()

    if msg ~= "" then
      message = msg
      progress = (percent or 1) % 100
    end

    if msg == "Downloading" then
      downloading = true
    end

    return
  end

  if time < 2.5 then
    return
  end

  reset()
end

function love.draw()
  if not logo then
    love.graphics.setBackgroundColor(0, 0, 0)
    logo = love.graphics.newImage('stackmachine/splash.png')
  end

  love.graphics.setColor(255, 255, 255, math.min(255, time * 200))

  local width = love.graphics.getWidth()
  local height = love.graphics.getHeight()

  if logo then
    love.graphics.draw(logo, width / 2 - logo:getWidth() / 2,
                       height / 2 - logo:getHeight() / 2)
  end

  if downloading then
    love.graphics.setColor(255, 255, 255)
    love.graphics.rectangle("line", 40, height - 75, width - 80, 10)
    love.graphics.rectangle("fill", 40, height - 75,  (width - 80) * progress / 100, 10)
    love.graphics.printf(message, 40, height - 55, width - 80, 'center')
  end
end
