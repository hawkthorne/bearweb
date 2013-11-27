require 'love.filesystem'

local json = require "sparkle/json"
local http = require "socket.http"
local ltn12 = require "ltn12"

local thread = love.thread.getThread()

while true do

  local encoded = thread:demand("request")
  local req = json.decode(encoded)

  if req.url and req.payload then
    local data = json.encode(req.payload)
    http.request {
      method = "POST",
      url = req.url,
      headers = {["content-type"] = "application/json", ["content-length"] = tostring(data:len()) },
      source = ltn12.source.string(data),
    }
  end
end
