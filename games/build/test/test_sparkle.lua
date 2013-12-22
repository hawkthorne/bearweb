local windows = require "sparkle/windows"

function test_windows_split()
  local dir, base = windows.split("C:\\foo\\bar\\foo.exe")
  assert_equal("foo.exe", base)
  assert_equal("C:\\foo\\bar", dir)
end
