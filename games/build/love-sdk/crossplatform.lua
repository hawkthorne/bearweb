require "love.timer"

local os = require "os"
local glove = require "stackmachine/glove"
local urllib = require "stackmachine/urllib"
local logging = require "stackmachine/logging"
local utils = require "stackmachine/utils"

local crossplatform = {}
local logger = logging.new('update')

function crossplatform.getApplicationPath(args)
  if #args < 2 then
    return ""
  end
  return args[2]
end

-- no op
function crossplatform.cleanup()
  local updatedir = love.filesystem.getSaveDirectory() .. "/updates"
  local oldgame = updatedir .. "/oldgame.love"
  local update = updatedir .. "/update.love"

  love.filesystem.remove(oldgame)
  love.filesystem.remove(update)
end

function crossplatform.getDownload(item)
  for i, platform in ipairs(item.platforms) do
    if platform.name == "crossplatform" then
      return platform
    end
  end
  return nil
end

function crossplatform.replace(download, oldpath, args, callback)
  glove.filesystem.mkdir("updates")

  local destination = love.filesystem.getSaveDirectory() .. "/updates"
  local lovefile = destination .. "/update.love"
  local item = download.files[1]

  urllib.retrieve(item.url, lovefile, item.length, callback)

  callback(false, "Installing", 25)

  callback(false, "Installing", 100)
end

return crossplatform
