local logging = require 'sparkle/logging'

function love.load(arg)
  local logger = logging.new('foo')
  logger:info("Successly started")
end

function love.update(dt)
end

function love.draw(dt)
  love.graphics.print("KID PIX", 30, 30)
end
