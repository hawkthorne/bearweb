local lovetest = require "test/lovetest"

function love.load(arg)
  love.filesystem.setIdentity('bearweb')
  lovetest.run()
end

